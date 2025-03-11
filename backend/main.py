# uvicorn main:app --host 0.0.0.0 --port 3300 --reload --log-level debug
# uvicorn main:app --host 0.0.0.0 --port 3300
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json

from services.paper_data.total_tickers import tech, retail, banks, build, oil
from services.multiplicators.multiplicators_db import MultiplicatorsDBManager
from services.dividends.dividends_db import DividendsDBManager
from services.paper_data.paper_data_db import PaperDataDBManager
from services.ichimoku.ichimoku_func import ichimoku_index_data
from services.cbr_keyrate import KeyRate
from services.cbr_parse_infl import fetch_inflation_table

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


app = FastAPI()


@app.get("/")
async def root():
    logger.debug("Handling request for root endpoint")
    return {"message": "Hello World"}


@app.get("/api/index_ichimoku/{ticker}/{period}", response_model=dict)
async def get_all_candles_for_ichimoku_by_period(ticker: str, period: str) -> dict:
    logger.debug(f"Fetching all candles by ticker: {ticker} for period: {period}")

    return ichimoku_index_data(ticker, period)


@app.get("/api/key_rate/{period}", response_model=dict)
async def get_key_rate(period: str) -> dict:
    logger.debug(f"Fetching keyRate for period: {period}")

    return KeyRate(period=period).get_key_rate()


@app.get("/api/inflation_table", response_model=dict)
async def get_inflation_table() -> dict:
    logger.debug("Fetching infl. table")
    return fetch_inflation_table()


@app.get("/api/paper_main_data/{ticker}", response_model=dict)
async def get_paper_main_data(ticker: str) -> dict:
    logger.debug("Fetching main data on paper")
    try:
        db_manager = PaperDataDBManager()
        data = db_manager.update_cache(ticker)
        return {"mainData": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dividend_data/{ticker}", response_model=dict)
async def get_dividends(ticker: str) -> dict:
    try:
        db_manager = DividendsDBManager()
        data = db_manager.update_cache(ticker)
        return {"dividends": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/multiplicators_data/{ticker}", response_model=dict)
async def get_multiplicators_data(ticker: str) -> dict:
    try:
        db_manager = MultiplicatorsDBManager()
        data = db_manager.update_cache(ticker)
        logger.debug(f"{data}")
        logger.debug(f"{type(data)}")
        return {"multiplicators": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sectors/", response_model=dict)
async def get_sectors() -> dict:
    result = {"tech": tech, "retail": retail, "banks": banks, "build": build, "oil": oil}

    return {"sectors": result}


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
