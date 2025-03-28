# uvicorn main:app --host 0.0.0.0 --port 3300 --reload --log-level debug
# uvicorn main:app --host 0.0.0.0 --port 3300
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import asyncio

from services.imoex_change import get_imoex_quote
from services.share_price import get_realtime_quote
from services.paper_data.ticker_table_db import TickerTableDBManager
from services.cbr_currency import Currency
from gdp import GdpData, ImoexData
from services.paper_data.total_tickers import tech, retail, banks, build, oil, sectors
from services.multiplicators.multiplicators_db import MultiplicatorsDBManager
from services.dividends.dividends_db import DividendsDBManager
from services.paper_data.paper_data_db import PaperDataDBManager
from services.ichimoku.ichimoku_func import ichimoku_index_data
from services.cbr_keyrate import KeyRate
from services.cbr_parse_infl import fetch_inflation_table

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

db_manager = TickerTableDBManager()  # ticker-figi-uid table


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


@app.get("/api/gdp/", response_model=dict)
async def get_gdp_data() -> dict:
    """
    Ключ "gdp" – массив объектов:
    { "year": число, "value": число }

    Ключ "imoex" – массив объектов:
    { "year": число, "close": число }
    """

    gdp = GdpData()
    imoex = ImoexData()

    res = {"gdp": gdp.get_total_gdp(2013)["gdp"], "imoex": imoex.get_imoex_data()["imoex"]}

    return res


@app.get("/api/gdp_sectors/", response_model=dict)
async def get_gdp_sectors() -> dict:
    """
    Ключи — названия отраслей экономики (секторов)
    {"oil": [
        {"year": 2013, "value": 100.947872},
        ...
    ],
    "build": [
        {"year": 2013, "value": 98.72644},
        ...
    ]}
    """
    gdp = GdpData()
    data = gdp.get_sectors_gdp()
    return data


@app.get("/api/currency/", response_model=dict)
async def get_currency() -> dict:
    """Возвращает данные в формате для трех валют:
    {
      "USD": 100.01,
      "EUR": 123.34,
      "CNY": 12.4,
      }
    """
    return Currency().get_data_on_currency()


@app.get("/api/share_price/{ticker}", response_model=dict)
async def websocket_share_price(ticker: str) -> dict:
    """
    Возвращает данные текущей котировки акции.
    {
      "price": текущая цена (float),
      "abs_change": абсолютное изменение (float),
      "percent_change": изменение в процентах (float)
    }
    """
    figi: str = db_manager.get_figi_by_ticker(ticker)
    if not figi:
        raise HTTPException(status_code=404, detail="Ticker not found")
    data = get_realtime_quote(figi)
    logger.debug(f"Ticker {ticker} c FIGI {figi}, data: {data}")
    return data


@app.get("/api/imoex_change/", response_model=dict)
async def get_imoex_data() -> dict:
    """
    Возвращает текущую котировку IMOEX:
      {
         "price": число,
         "abs_change": число,
         "percent_change": число
      }
    """
    try:
        data = get_imoex_quote()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
