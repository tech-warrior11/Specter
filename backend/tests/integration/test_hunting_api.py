import pytest
import pytest_asyncio
import uuid
from httpx import AsyncClient, ASGITransport
from datetime import datetime, timezone
from app.main import app
from app.database.database import AsyncSessionLocal
from app.models.event import Event


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        async with AsyncSessionLocal() as session:
            evt = Event(
                id=f"evt-hunt-test-{uuid.uuid4().hex[:8]}",
                timestamp=datetime.now(timezone.utc),
                source="linux-auth",
                event_type="authentication",
                action="login_failed",
                user_identity="suspicious_admin",
                source_ip="10.10.99.88",
                severity="high",
                raw_event={}
            )
            session.add(evt)
            await session.commit()
        yield c


@pytest.mark.asyncio
async def test_threat_hunt_dsl_query(client: AsyncClient):
    payload = {
        "query": 'user = "suspicious_admin" AND severity = "high"',
        "time_window_hours": 48
    }
    response = await client.post("/api/hunting/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_matches"] >= 1
    assert data["events"][0]["user"] == "suspicious_admin"
    assert "user:suspicious_admin" in data["suggested_pivots"]
