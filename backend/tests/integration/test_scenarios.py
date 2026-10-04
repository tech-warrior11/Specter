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
async def test_list_and_run_multi_stage_scenario(client: AsyncClient):
    # 1. List scenarios
    list_res = await client.get("/api/scenarios")
    assert list_res.status_code == 200
    scenarios = list_res.json()
    assert len(scenarios) >= 5

    # 2. Run multi-stage scenario
    run_res = await client.post("/api/scenarios/SCENARIO-MULTI-001/run")
    assert run_res.status_code == 200
    result = run_res.json()
    assert result["status"] == "COMPLETED_SUCCESSFULLY"
    assert result["events_generated_count"] == 10
    assert result["alerts_triggered_count"] >= 3
    assert result["investigation_id"] is not None
    assert "Security Investigation Narrative" in result["security_story"]

    # 3. Verify Investigation Workbench endpoint
    inv_id = result["investigation_id"]
    wb_res = await client.get(f"/api/investigations/{inv_id}")
    assert wb_res.status_code == 200
    wb = wb_res.json()
    assert wb["id"] == inv_id
    assert len(wb["timeline"]) >= 3


@pytest.mark.asyncio
async def test_training_mode_submission(client: AsyncClient):
    submission = {
        "suspect_entity": "198.51.100.25",
        "initial_access_method": "Brute Force Authentication",
        "attack_chain_tactic": "Credential Access -> Execution -> Exfiltration",
        "evidence_justification": "Observed 5 failed logins followed by successful login from 198.51.100.25"
    }

    res = await client.post("/api/scenarios/SCENARIO-MULTI-001/training_submit", json=submission)
    assert res.status_code == 200
    data = res.json()
    assert data["score"] >= 70
    assert data["grade"] == "Pass"
