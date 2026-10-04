import pytest
from app.config import Settings


def test_settings_initialization(test_settings: Settings):
    assert test_settings.APP_NAME == "Specter Test Suite"
    assert test_settings.ENVIRONMENT == "testing"
    assert test_settings.USE_IN_MEMORY_GRAPH is True
    assert test_settings.JWT_ALGORITHM == "HS256"


def test_cors_origins_parsing():
    s = Settings(CORS_ORIGINS="http://localhost:3000, http://example.com")
    assert isinstance(s.CORS_ORIGINS, list)
    assert len(s.CORS_ORIGINS) == 2
    assert "http://localhost:3000" in s.CORS_ORIGINS
    assert "http://example.com" in s.CORS_ORIGINS
