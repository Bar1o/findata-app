from sqlalchemy import Column, Integer, String, Float, DateTime, create_engine, Enum, UniqueConstraint
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
import enum

Base = declarative_base()


class PeriodEnum(enum.Enum):
    D = "D"
    M = "M"
    Y = "Y"
    _5Y = "5Y"
    _10Y = "10Y"


class InflationTable(Base):
    __tablename__ = "inflation_table"
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(String, unique=True)
    keyRate = Column(Float)
    infl = Column(Float)
    targetInfl = Column(Float)
    last_updated = Column(DateTime, default=datetime.now())


class KeyRateTable(Base):
    __tablename__ = "key_rate_table"
    id = Column(Integer, primary_key=True, autoincrement=True)
    period = Column(Enum(PeriodEnum), nullable=False)
    date = Column(DateTime, nullable=False)
    rate = Column(Float)
    last_updated = Column(DateTime, default=datetime.now())

    __table_args__ = (UniqueConstraint("period", "date", name="uix_period_date"),)


DATABASE_URL = "sqlite:///./db/database.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)
