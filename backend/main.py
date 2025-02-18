# uvicorn main:app --host 0.0.0.0 --port 3300 --reload --log-level debug
# uvicorn main:app --host 0.0.0.0 --port 3300
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import uvicorn

from services.ichimoku_idx import IchimokuIndex
from services.cbr_keyrate import KeyRate
from services.cbr_parse_infl import fetch_inflation_table
from services.paper_data import PaperData

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


app = FastAPI()


@app.get("/")
async def root():
    logger.debug("Handling request for root endpoint")
    return {"message": "Hello World"}


@app.get("/api/index_ichimoku/{figi}/{period}", response_model=dict)
async def get_all_candles_for_ichimoku_by_period(figi: str, period: str) -> dict:
    logger.debug(f"Fetching all candles by figi: {figi} for period: {period}")

    return IchimokuIndex(figi=figi, period=period).get_exported_data()


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
    # return PaperData().export_main_data_json(ticker=ticker)
    return {
        "mainData": {
            "ticker": "SBER",
            "figi": "BBG004730N88",
            "isin": "RU0009029540",
            "issue_size": {"units": 21586948000, "nano": 0},
            "nominal": {"units": 3, "nano": 0},
            "nominal_currency": "RUB",
            "primary_index": "IMOEX Index",
            "preferred_share_type": "",
            "ipo_date": "2007-07-11T00:00:00Z",
            "registry_date": "2007-07-11T00:00:00Z",
            "issue_kind": "non_documentary",
            "placement_date": "2007-07-18T00:00:00Z",
            "repres_isin": "",
            "issue_size_plan": {"units": 21586948000, "nano": 0},
            "total_float": {"units": 10361735040, "nano": 0},
        }
    }


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
