import pytest
import pytest_asyncio
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.models import Base
from app.models.event import Event
from app.services.detection import detection_engine


@pytest_asyncio.fixture
async def test_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    sm = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with sm() as session:
        await detection_engine.sync_rules_to_db(session)
        yield session
    await engine.dispose()


@pytest.mark.asyncio
async def test_auth_brute_force_detection(test_session: AsyncSession):
    # Inject 5 failed logins from same IP for same user
    alerts_total = []
    for i in range(5):
        evt = Event(
            id=f"evt-test-fail-{i}",
            timestamp=datetime.now(timezone.utc),
            source="linux-auth",
            event_type="authentication",
            action="login_failed",
            user_identity="victim",
            source_ip="192.168.1.100",
            severity="medium",
            raw_event={}
        )
        test_session.add(evt)
        alerts = await detection_engine.evaluate_event(test_session, evt)
        alerts_total.extend(alerts)

    assert len(alerts_total) >= 1
    rule_ids = [a.rule_id for a in alerts_total]
    assert "DET-AUTH-001" in rule_ids


@pytest.mark.asyncio
async def test_suspicious_process_detection(test_session: AsyncSession):
    evt = Event(
        id="evt-proc-01",
        timestamp=datetime.now(timezone.utc),
        source="sysmon",
        event_type="process",
        action="process_created",
        user_identity="alice",
        host="WORKSTATION-01",
        process_name="powershell.exe",
        severity="medium",
        raw_event={}
    )
    test_session.add(evt)
    alerts = await detection_engine.evaluate_event(test_session, evt)

    rule_ids = [a.rule_id for a in alerts]
    assert "DET-EXEC-001" in rule_ids
