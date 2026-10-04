import pytest
import os
import sys

# Ensure backend root directory is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.config import settings, Settings


@pytest.fixture
def test_settings() -> Settings:
    return Settings(
        ENVIRONMENT="testing",
        APP_NAME="Specter Test Suite",
        JWT_SECRET="test-super-secret-key-32-chars-long-specter!",
        USE_IN_MEMORY_GRAPH=True,
        DATABASE_URL="sqlite+aiosqlite:///:memory:",
        POSTGRES_DATABASE_URL="sqlite+aiosqlite:///:memory:"
    )
