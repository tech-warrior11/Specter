import pytest
import pytest_asyncio
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.models import Base
from app.models.event import Event
from app.services.behavior import behavior_engine


@pytest_asyncio.fixture
async def test_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    sm = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with sm() as session:
        yield session
    await engine.dispose()


@pytest.mark.asyncio
async def test_off_hours_behavior_anomaly(test_session: AsyncSession):
    # Establish baseline profile for user bob: normal hours [9, 10, 11, 12, 13, 14, 15, 16, 17]
    profile = await behavior_engine.build_or_update_profile(test_session, "user:bob", profile_type="user")
    assert profile.normal_login_hours is not None

    # Trigger event at 3 AM UTC (off-hours)
    off_hour_dt = datetime(2026, 9, 30, 3, 15, 0, tzinfo=timezone.utc)
    evt = Event(
        id="evt-ano-01",
        timestamp=off_hour_dt,
        source="linux-auth",
        event_type="authentication",
        action="login_success",
        user_identity="bob",
        host="LAB-01",
        severity="low",
        raw_event={}
    )
    test_session.add(evt)
    await test_session.commit()

    anomalies = await behavior_engine.evaluate_anomalies(test_session, evt)
    assert len(anomalies) >= 1
    assert anomalies[0].anomaly_type == "time_of_day_deviation"
    assert "bob" in anomalies[0].explanation
