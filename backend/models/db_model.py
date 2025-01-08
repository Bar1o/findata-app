from sqlalchemy import Column, Integer, String, Float, DateTime, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

Base = declarative_base()


class InflationTable(Base):
    __tablename__ = "inflation_table"
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(String, unique=True)
    keyRate = Column(Float)
    infl = Column(Float)
    targetInfl = Column(Float)
    last_updated = Column(DateTime, default=datetime.utcnow)


DATABASE_URL = "sqlite:///./db/database.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)
