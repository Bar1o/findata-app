import pytest
import sys
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.models.db_model import Base


@pytest.fixture(scope="session")
def test_engine():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    yield engine


@pytest.fixture(autouse=True, scope="session")
def override_db_engine(test_engine):
    import backend.models.db_model as db_mod

    db_mod.engine = test_engine
    db_mod.SessionLocal = sessionmaker(bind=test_engine)
    yield


@pytest.fixture
def test_db_session(test_engine):
    TestingSessionLocal = sessionmaker(bind=test_engine)
    session = TestingSessionLocal()
    yield session
    session.rollback()
    session.close()
