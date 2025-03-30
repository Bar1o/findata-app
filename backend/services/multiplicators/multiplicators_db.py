from pydantic import BaseModel
from datetime import datetime, timedelta
import json

from models.db_model import SessionLocal, MultiplicatorsCache
from services.multiplicators.multiplicators import Multiplicators
from ..paper_data.total_tickers import missing_tickers, api_tickers, all_tickers
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class MultiplicatorsDBManager(BaseModel):
    """
    Класс для управления сохранением и обновлением кэша данных по мультипликаторам.

    При вызове проверяется наличие кэшированных данных по мультипликаторам (полученных
    через метод get_multiplicator_data_from_api). Если сохранённые данные старше, чем cache_duration,
    происходит их обновление и сохранение в БД.
    """

    cache_duration: timedelta = timedelta(days=90)

    def get_session(self):
        """
        Возвращает сессию для работы с базой данных.
        """
        return SessionLocal()

    def get_cache(self, ticker: str) -> dict | None:
        """
        Получает кэшированные данные по мультипликаторам для указанного тикера.

        Если найден кэш и разница между текущим временем и временем обновления кэша
        меньше, чем cache_duration, возвращается словарь с данными.
        Иначе возвращается None.
        """
        session = self.get_session()
        try:
            cache = session.query(MultiplicatorsCache).filter(MultiplicatorsCache.ticker == ticker).first()
            if cache and (datetime.now() - cache.timestamp) < self.cache_duration:
                return json.loads(cache.data)
            return None
        finally:
            session.close()

    def save_cache(self, ticker: str, data: dict) -> None:
        """
        Сохраняет данные по мультипликаторам для указанного тикера в кэше.

        Данные сериализуются в JSON-формате, а время обновления устанавливается равным текущему.
        """
        session = self.get_session()
        try:
            cache = MultiplicatorsCache(ticker=ticker, data=json.dumps(data, default=str), timestamp=datetime.now())
            session.merge(cache)
            session.commit()
        finally:
            session.close()

    def update_cache(self, ticker: str) -> dict:
        """
        Возвращает данные по мультипликаторам для заданного тикера.

        Если существует действующий кэш (возраст которого меньше cache_duration),
        он возвращается. Иначе данные запрашиваются через Multiplicators API, сохраняются и возвращаются.
        """
        self.clear_outdated_cache()

        cached_data = self.get_cache(ticker)
        logger.debug(f"cached data is None:{cached_data is None}")
        if cached_data is not None:
            return cached_data

        all_data = Multiplicators().get_multiplicator_data_from_api()
        new_data = all_data.get(ticker, {})

        self.save_cache(ticker, new_data)
        return new_data

    def clear_outdated_cache(self) -> None:
        """
        Удаляет устаревшие записи кэша из базы данных.

        Записи считаются устаревшими, если их возраст превышает cache_duration.
        """
        session = self.get_session()
        try:
            outdated_time = datetime.now() - self.cache_duration
            session.query(MultiplicatorsCache).filter(MultiplicatorsCache.timestamp < outdated_time).delete()
            session.commit()
        finally:
            session.close()
