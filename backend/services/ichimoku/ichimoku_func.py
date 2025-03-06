import logging
import json

from fastapi import HTTPException

from services.ichimoku.ichimoku_db import IchimokuDbManager

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def ichimoku_index_data(ticker: str, period: str):
    db_manager = IchimokuDbManager(ticker=ticker, period=period)
    cache = db_manager.get_cache()

    if cache:  # check for valid cache
        data = json.loads(cache.data)
        logger.debug("Returning data from cache")
        return {"data": data}

    try:
        db_manager.update_cache()
        cache = db_manager.get_cache()
        if cache:
            data = json.loads(cache.data)
            logger.debug("Returning newly updated data")
            return {"data": data}
        else:
            raise HTTPException(status_code=500, detail="Cache update failed")
    except Exception as e:
        logger.error(f"Error updating cache: {e}")
        raise HTTPException(status_code=500, detail="Internal server error. Can't get any ichimoku data")
