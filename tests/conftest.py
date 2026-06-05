import os

os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["SECRET_KEY"] = "testing"
os.environ["EMAIL_ENABLED"] = "False"
os.environ["AI_ENABLED"] = "False"

from app.db.session import engine, Base
from app.main import app
import pytest


@pytest.fixture(scope="session", autouse=True)
def prepare_test_db():
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def client():
    from fastapi.testclient import TestClient

    return TestClient(app)
