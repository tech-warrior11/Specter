import pytest
import pytest_asyncio
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.models import Base
from app.models.investigation import Investigation
from app.models.event import Event
from app.models.alert import Alert
from app.schemas.investigation import EvidenceCreate
from app.services.investigation import investigation_service


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
async def test_evidence_attachment_with_sha256(test_session: AsyncSession):
    inv = Investigation(title="Test Case", root_entities=["user:victim"])
    test_session.add(inv)
    await test_session.commit()

    evidence_in = EvidenceCreate(
        evidence_type="log_snippet",
        source="linux-auth",
        description="Raw authentication logs",
        content_text="Failed password for invalid user admin from 10.10.10.50"
    )

    evi = await investigation_service.attach_evidence(test_session, inv.id, evidence_in, collector="analyst1")
    assert evi.id.startswith("evi-")
    assert len(evi.sha256) == 64
    assert evi.collector_user == "analyst1"


def test_security_story_generation():
    ev1 = Event(
        id="evt-001",
        timestamp=datetime.now(timezone.utc),
        source="linux-auth",
        event_type="authentication",
        action="login_failed",
        user_identity="testuser",
        source_ip="198.51.100.25",
        severity="medium",
        raw_event={}
    )
    ev2 = Event(
        id="evt-002",
        timestamp=datetime.now(timezone.utc),
        source="linux-auth",
        event_type="authentication",
        action="login_success",
        user_identity="testuser",
        host="LAB-PC-01",
        severity="high",
        raw_event={}
    )
    ev3 = Event(
        id="evt-003",
        timestamp=datetime.now(timezone.utc),
        source="sysmon",
        event_type="process",
        action="process_created",
        user_identity="testuser",
        host="LAB-PC-01",
        process_name="powershell.exe",
        severity="high",
        raw_event={}
    )

    story = investigation_service.generate_security_story([ev1, ev2, ev3], [])
    assert "authentication failure" in story.lower()
    assert "successful authentication" in story.lower()
    assert "process execution event" in story.lower()
    assert "evt-001" in story
    assert "evt-002" in story
    assert "evt-003" in story
