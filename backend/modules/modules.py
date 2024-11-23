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
    Time: str
    Open: float
    Close: float
    Max: float
    Min: float
    Volume: int
    Tenkan_sen: float = None
    Kijun_sen: float = None
    Senkou_Span_A: float = None
    Senkou_Span_B: float = None
    Chikou_Span: float = None


all_figi_by_ticker: dict[str:str] = {
    "SBER": "BBG004730N88",
    "GAZP": "BBG004731354",
}
