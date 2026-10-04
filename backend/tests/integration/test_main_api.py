import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_health_endpoint(async_client: AsyncClient):
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "app" in data
    assert response.headers.get("x-content-type-options") == "nosniff"
    assert response.headers.get("x-frame-options") == "DENY"


@pytest.mark.asyncio
async def test_ready_endpoint(async_client: AsyncClient):
    response = await async_client.get("/ready")
    assert response.status_code == 200
    assert response.json()["ready"] is True


@pytest.mark.asyncio
async def test_metrics_endpoint(async_client: AsyncClient):
    response = await async_client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "events_processed" in data
    assert "alerts_generated" in data
