from pydantic import BaseModel
from datetime import datetime, timedelta
import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from models.db_model import SessionLocal, PECache, SectorPECache
from .parse_pe import ParsePE

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class PeDBManager(BaseModel):
    """
    Менеджер для работы с P/E данными компаний и расчётом среднего P/E для сектора.
    Данные считаются устаревшими, если их возраст более 3 месяцев.
    """

    cache_duration: timedelta = timedelta(days=90)  # 3 месяца
    parser: ParsePE = ParsePE()

    def get_session(self):
        return SessionLocal()

    def _rename_pe_field(self, data: dict) -> dict:
        # Если данные содержат ключ "P/E", заменяем его на "p_e"
        if data and "P/E" in data:
            data["p_e"] = data.pop("P/E")
        return data

    def get_company_pe(self, ticker: str) -> dict | None:
        """
        Получить P/E данных компании по тикеру.
        Если данные устарели, происходит их обновление.
        """
        session = self.get_session()
        try:
            record = session.query(PECache).filter(PECache.ticker == ticker).first()
            if record:
                age = datetime.now() - record.timestamp
                if age < self.cache_duration:
                    result = json.loads(record.data)
                    return self._rename_pe_field(result)
                else:
                    return self.update_company_pe(ticker)
            else:
                return self.update_company_pe(ticker)
        finally:
            session.close()

    def get_sector_mean_pe(self, sector: str) -> dict | None:
        """
        Получить среднее P/E сектора.
        Если кэш актуален (младше 90 дней), данные берутся из БД,
        иначе пересчитываются и сохраняются.
        """
        sector_lower = sector.lower()
        session = self.get_session()
        try:
            record = session.query(SectorPECache).filter(SectorPECache.sector == sector_lower).first()
            if record:
                age = datetime.now() - record.timestamp
                if age < self.cache_duration:
                    result = json.loads(record.data)
                    return self._rename_pe_field(result)
                else:
                    return self.update_sector_pe(sector)
            else:
                return self.update_sector_pe(sector)
        finally:
            session.close()

    def update_company_pe(self, ticker: str) -> dict:
        """
        Обновить данные P/E компании, используя метод парсинга.
        """
        pe_data = self.parser.parse_pe_by_ticker(ticker)
        pe_data = self._rename_pe_field(pe_data)
        self.save_company_pe(ticker, pe_data)
        return pe_data

    def update_sector_pe(self, sector: str) -> dict:
        """
        Рассчитать и сохранить среднее P/E для сектора.
        Параллельно запрашивает данные по каждому тикеру сектора.
        """
        sector_lower = sector.lower()
        tickers = self.parser.sector_tickers.get(sector_lower)
        if not tickers:
            logger.error(f"Сектор {sector} не найден в sector_tickers.")
            return {}

        results = {}
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_ticker = {executor.submit(self.get_company_pe, ticker): ticker for ticker in tickers}
            for future in as_completed(future_to_ticker):
                ticker = future_to_ticker[future]
                try:
                    data = future.result()
                    if data and "p_e" in data:
                        results[ticker] = data
                except Exception as e:
                    logger.error(f"Ошибка получения P/E для {ticker}: {e}")

        if not results:
            logger.error("Не удалось получить данные ни для одного тикера сектора.")
            return {}

        summed = None
        counts = None
        # Для каждого тикера суммируем значения и считаем кол-во валидных значений по каждому году отдельно
        for data in results.values():
            pe_values = data.get("p_e")
            if pe_values:
                if summed is None:
                    summed = [0.0] * len(pe_values)
                    counts = [0] * len(pe_values)
                for i, pe in enumerate(pe_values):
                    if pe is not None:
                        summed[i] += pe
                        counts[i] += 1

        if summed is None or all(c == 0 for c in counts):
            logger.error("Нет данных для расчёта среднего P/E.")
            return {}

        mean_pe = [round(s / c, 2) if c != 0 else None for s, c in zip(summed, counts)]
        sample = next(iter(results.values()))
        years = sample.get("year", [])
        mean_data = {"year": years, "P/E": mean_pe, "year_change": sample.get("year_change", [])}
        mean_data = self._rename_pe_field(mean_data)

        self.save_sector_pe(sector_lower, mean_data)
        return mean_data

    def save_company_pe(self, ticker: str, data: dict) -> None:
        session = self.get_session()
        try:
            record = PECache(ticker=ticker, data=json.dumps(data, default=str), timestamp=datetime.now())
            session.merge(record)
            session.commit()
        finally:
            session.close()

    def save_sector_pe(self, sector: str, data: dict) -> None:
        session = self.get_session()
        try:
            record = SectorPECache(sector=sector, data=json.dumps(data, default=str), timestamp=datetime.now())
            session.merge(record)
            session.commit()
        finally:
            session.close()

    def clear_outdated_cache(self) -> None:
        """
        Удаляет записи, добавленные более 3 месяцев назад.
        """
        outdated_time = datetime.now() - self.cache_duration
        session = self.get_session()
        try:
            deleted_companies = session.query(PECache).filter(PECache.timestamp < outdated_time).delete()
            deleted_sectors = session.query(SectorPECache).filter(SectorPECache.timestamp < outdated_time).delete()
            session.commit()
            logger.debug(f"Deleted {deleted_companies} old company PE records and {deleted_sectors} old sector records.")
        finally:
            session.close()


man = PeDBManager()

print(man.get_company_pe("SBER"))
print(man.get_sector_mean_pe("banks"))
