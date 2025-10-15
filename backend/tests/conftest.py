"""
Pytest configuration and fixtures.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.config import get_settings


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def settings():
    """Get application settings."""
    return get_settings()


@pytest.fixture
def sample_tickers():
    """Sample tickers for testing."""
    return ["AAPL", "MSFT", "GOOGL", "AMZN"]


@pytest.fixture
def date_range():
    """Sample date range for testing."""
    return {
        "start_date": "2023-01-01",
        "end_date": "2023-12-31"
    }
