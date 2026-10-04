import uuid
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
async def test_user_registration_and_jwt_auth(client: AsyncClient):
    uid = uuid.uuid4().hex[:8]
    username = f"hunter_{uid}"
    email = f"hunter_{uid}@specter.local"
    password = "SuperSecurePassword123!"

    reg_payload = {
        "username": username,
        "email": email,
        "password": password,
        "role": "THREAT_HUNTER"
    }
    reg_res = await client.post("/api/auth/register", json=reg_payload)
    assert reg_res.status_code == 201

    login_payload = {
        "username": username,
        "password": password
    }
    login_res = await client.post("/api/auth/login", json=login_payload)
    assert login_res.status_code == 200
    token_data = login_res.json()
    assert "access_token" in token_data
    assert token_data["role"] == "THREAT_HUNTER"

    # Authenticated /me request
    me_res = await client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token_data['access_token']}"}
    )
    assert me_res.status_code == 200
    assert me_res.json()["username"] == username
