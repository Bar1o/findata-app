# python -m services.dividends.dividends_db
from pydantic import BaseModel
from datetime import datetime, timedelta
import json

from models.db_model import SessionLocal, DividendsCache
from services.dividends.dividends import get_extended_dividend_data_by_ticker


class DividendsDBManager(BaseModel):
    """
    Класс для управления сохранением и обновлением кэша данных по дивидендам.

    При обращении проверяет, сохранены ли данные по дивидендам для указанного тикера,
    и если время с момента последнего обновления превышает один день, получает новые данные,
    сохраняет их и возвращает обновлённый кэш.
    """

    cache_duration: timedelta = timedelta(days=90)

    def get_session(self):
        """
        Возвращает сессию для работы с базой данных.
        """
        return SessionLocal()

    def get_cache(self, ticker: str) -> dict | None:
        """
        Получает кэшированные данные по дивидендам для указанного тикера.

        Если найден кэш и разница между текущим временем и временем обновления кэша
        меньше одного дня, возвращает данные кэша (в виде словаря).
        Иначе возвращает None.
        """
        session = self.get_session()
        try:
            cache = session.query(DividendsCache).filter(DividendsCache.ticker == ticker).first()
            # если найден кэш и его возраст меньше cache_duration (90 дней)
            if cache and (datetime.now() - cache.timestamp) < self.cache_duration:
                return json.loads(cache.data)
            return None
        finally:
            session.close()

    def save_cache(self, ticker: str, data: dict) -> None:
        """
        Сохраняет данные по дивидендам для указанного тикера в кэше.

        Данные сериализуются в формате JSON, а также сохраняется текущее время обновления.
        """
        session = self.get_session()
        try:
            cache = DividendsCache(
                ticker=ticker, data=json.dumps(data, default=str), timestamp=datetime.now()  # default=str преобразует datetime в строку
            )
            session.merge(cache)
            session.commit()
        finally:
            session.close()

    def update_cache(self, ticker: str) -> dict:
        """
        Возвращает данные по дивидендам для указанного тикера.

        Если кэш существует и данные обновлены менее одного дня назад, возвращает кэшированные данные.
        Иначе вызывается функция получения новых данных, результат сохраняется в кэш и возвращается.
        """
        self.clear_outdated_cache()

        cached_data = self.get_cache(ticker)
        if cached_data is not None:
            return cached_data

        new_data = get_extended_dividend_data_by_ticker(ticker=ticker)
        self.save_cache(ticker, new_data)
        return new_data

    def clear_outdated_cache(self) -> None:
        """
        Удаляет устаревшие записи кэша из базы данных.

        Записи считаются устаревшими, если время их обновления более одного дня назад.
        """
        session = self.get_session()
        try:
            outdated_time = datetime.now() - self.cache_duration
            session.query(DividendsCache).filter(DividendsCache.timestamp < outdated_time).delete()
            session.commit()
        finally:
            session.close()


# db = DividendsDBManager()
# print(db.update_cache("OZON"))
