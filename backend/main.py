# uvicorn main:app --host 0.0.0.0 --port 3300 --reload --log-level debug
# uvicorn main:app --host 0.0.0.0 --port 3300
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models.models import Figi, all_figi_by_ticker, Candle, IchimokuCandle
from typing import List
import uvicorn

from all_candles import get_all_candles_by_figi, get_all_candles_by_period
from cbr_keyrate import KeyRate

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


app = FastAPI()


temp_figi = Figi(figi=all_figi_by_ticker["SBER"])
figi = "BBG004730N88"


@app.get("/")  # отправить на фронт
async def root():
    logger.debug("Handling request for root endpoint")
    return {"message": "Hello World"}


# TODO: добавление новых тикеров
# @app.post("/ticker_data")
# async def create_item(ticker: TickerPrice):
#     ticker_data.append(ticker)
#     logger.debug(f"Received item: {ticker}")
#     return ticker_data


@app.get("/api/index_ichimoku/{figi}", response_model=dict)
async def get_data_for_ichimoku(figi: str) -> dict:
    logger.debug(f"Fetching all candles by figi: {figi}")

    return {"data": get_all_candles_by_figi(figi)}


@app.get("/api/index_ichimoku/{figi}/{period}", response_model=dict)
async def get_all_candles_for_ichimoku_by_period(figi: str, period: str) -> dict:
    logger.debug(f"Fetching all candles by figi: {figi} for period: {period}")

    return get_all_candles_by_period(figi, period)


@app.get("/api/key_rate/{period}", response_model=dict)
async def get_key_rate(period: str) -> dict:
    logger.debug(f"Fetching keyRate for period: {period}")

    return KeyRate(period=period).get_key_rate()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3001",
        "https://findata.vabarnis.ru",
        "http://findata.vabarnis.ru",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
