import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database.database import init_db


@pytest_asyncio.fixture
async def client():
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.mark.asyncio
async def test_single_event_ingestion_and_retrieval(client: AsyncClient):
    payload = {
        "source": "linux-auth",
        "event_type": "authentication",
        "action": "login_failed",
        "user": "victim_user",
        "host": "LAB-PC-99",
        "source_ip": "192.168.1.50",
        "severity": "medium"
    }

    response = await client.post("/api/events", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"].startswith("evt-")
    assert data["user_identity"] == "victim_user"
    assert data["host"] == "LAB-PC-99"

    # Query events list
    list_res = await client.get("/api/events?user=victim_user")
    assert list_res.status_code == 200
    events = list_res.json()
    assert len(events) >= 1
    assert events[0]["user_identity"] == "victim_user"

    # Query created entity
    ent_res = await client.get("/api/entities/user:victim_user/profile")
    assert ent_res.status_code == 200
    profile = ent_res.json()
    assert profile["entity"]["id"] == "user:victim_user"


@pytest.mark.asyncio
async def test_bulk_event_ingestion(client: AsyncClient):
    bulk_payload = {
        "events": [
            {
                "source": "sysmon",
                "event_type": "process",
                "action": "process_created",
                "user": "alice",
                "host": "HOST-01",
                "process": "cmd.exe",
                "severity": "low"
            },
            {
                "source": "sysmon",
                "event_type": "process",
                "action": "process_created",
                "user": "alice",
                "host": "HOST-01",
                "process": "whoami.exe",
                "parent_process": "cmd.exe",
                "severity": "medium"
            }
        ]
    }

    response = await client.post("/api/events/bulk", json=bulk_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["received_count"] == 2
    assert data["ingested_count"] == 2
    assert len(data["event_ids"]) == 2
