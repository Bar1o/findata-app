import logging
from fastapi import FastAPI, HTTPException
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import asyncio

from services.pe.pe_db_manager import PeDBManager
from services.imoex_change import get_imoex_quote
from services.share_price import get_realtime_quote
from services.paper_data.ticker_table_db import TickerTableDBManager
from services.cbr_currency import Currency
from services.gdp import GdpData, ImoexData
from services.paper_data.total_tickers import tech, retail, banks, build, oil, sectors, sectors_companies
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
    result = await run_in_threadpool(lambda: KeyRate(period=period).get_key_rate())
    return result


@app.get("/api/inflation_table/", response_model=dict)
async def get_inflation_table() -> dict:
    logger.debug("Fetching infl. table")
    # запускаем синхронную функцию в пуле потоков
    result = await run_in_threadpool(fetch_inflation_table)
    return result


@app.get("/api/paper_main_data/{ticker}", response_model=dict)
async def get_paper_main_data(ticker: str) -> dict:
    logger.debug("Fetching main data on paper")
    try:
        db_manager = PaperDataDBManager()
        data = await run_in_threadpool(db_manager.update_cache, ticker)
        return {"mainData": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dividend_data/{ticker}", response_model=dict)
async def get_dividends(ticker: str) -> dict:
    try:
        db_manager = DividendsDBManager()
        data = await run_in_threadpool(db_manager.update_cache, ticker)
        return {"dividends": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/multiplicators_data/{ticker}", response_model=dict)
async def get_multiplicators_data(ticker: str) -> dict:
    try:
        db_manager = MultiplicatorsDBManager()
        data = await run_in_threadpool(db_manager.update_cache, ticker)
        logger.debug(f"{data}")
        logger.debug(f"{type(data)}")
        return {"multiplicators": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sectors/", response_model=dict)
async def get_sectors() -> dict:
    return {"sectors": sectors_companies}


@app.get("/api/gdp/", response_model=dict)
async def get_gdp_data() -> dict:
    """
    Ключ "gdp" – массив объектов:
    { "year": число, "value": число }
    Ключ "imoex" – массив объектов:
    { "year": число, "close": число }
    """

    def get_data():
        gdp = GdpData()
        imoex = ImoexData()
        return {"gdp": gdp.get_total_gdp(2013)["gdp"], "imoex": imoex.get_imoex_data()["imoex"]}

    result = await run_in_threadpool(get_data)
    return result


@app.get("/api/gdp_sectors/", response_model=dict)
async def get_gdp_sectors() -> dict:
    def get_data():
        gdp = GdpData()
        return gdp.get_sectors_gdp()

    result = await run_in_threadpool(get_data)
    return result


@app.get("/api/currency/", response_model=dict)
async def get_currency() -> dict:
    result = await run_in_threadpool(lambda: Currency().get_data_on_currency())
    return result


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
    data = await run_in_threadpool(get_realtime_quote, figi)
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
        data = await run_in_threadpool(get_imoex_quote)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/pe/{ticker}", response_model=dict)
async def get_pe_on_comp(ticker: str) -> dict:
    """Возвращает данные вида:
    {"company":
        {
        'year': [2020, 2021, 2022, 2023, 2024],
        'p_e': [8.0, 5.28, 11.8, 4.06, 3.99],
        'year_change': [0.18, -0.34, 1.23, -0.66, -0.02]
        },
    "mean": {
            ...
        }
    }
    """
    man = PeDBManager()
    sector = ""
    for sec in sectors_companies:
        if ticker in sectors_companies[sec]:
            print(sectors_companies)
            sector = sec
            print(sec)
            break
    result = {"ticker": man.get_company_pe(ticker), "mean": man.get_sector_mean_pe(sector)}

    return result


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3001",
        "http://localhost:3000",
        "https://findata.vabarnis.ru",
        "http://findata.vabarnis.ru",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=3300, reload=True, log_level="debug")
