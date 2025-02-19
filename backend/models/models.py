from pydantic import BaseModel
from datetime import datetime


class Quotation(BaseModel):
    units: int
    nano: int


factor: int = 1_000_000_000


def convert_quotation(q: Quotation):
    res = q.units + q.nano / factor
    if q.nano == 0:
        return int(res)
    return float(res)


class Window(BaseModel):
    small: int
    medium: int
    large: int


class Candle(BaseModel):
    time: datetime
    open: Quotation
    close: Quotation
    max: Quotation
    min: Quotation
    volume: int


class Figi(BaseModel):
    figi: str
    ticker: str = None


class IchimokuCandle(BaseModel):
    time: str
    open: float
    close: float
    high: float
    low: float
    volume: int
    tenkan_sen: float = None
    kijun_sen: float = None
    senkou_span_A: float = None
    senkou_span_B: float = None
    chikou_span: float = None


class DBManager(BaseModel):
    def get_cache():
        pass

    def save_cache():
        pass

    def update_cache():
        pass

    def clear_outdated_cache():
        pass


all_figi_by_ticker: dict[str:str] = {
    "SBER": "BBG004730N88",
    "GAZP": "BBG004731354",
}
