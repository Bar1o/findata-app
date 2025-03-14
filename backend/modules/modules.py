from pydantic import BaseModel
from datetime import datetime


class Quotation(BaseModel):
    units: int
    nano: int


factor: int = 1_000_000_000


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


all_figi_by_ticker: dict[str:str] = {
    "SBER": "BBG004730N88",
    "GAZP": "BBG004731354",
}
