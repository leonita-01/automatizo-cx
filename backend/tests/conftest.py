import pytest
from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app
from app.security.rate_limit import rate_limiter


@pytest.fixture(autouse=True)
def clean_database():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    rate_limiter.reset()
    yield


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def admin_headers():
    return {"X-Admin-Key": "change-me-before-production"}
