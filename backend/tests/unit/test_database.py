import pytest
import pytest_asyncio
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.models import (
    Base, User, Event, Entity, EntityRelationship, DetectionRule,
    Alert, Investigation, Incident, Evidence, IOC, BehaviorProfile,
    Anomaly, HuntQuery, AuditLog
)


@pytest_asyncio.fixture
async def test_db_session():
    # Use SQLite in-memory for testing
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_create_user(test_db_session: AsyncSession):
    user = User(
        username="sec_hunter",
        email="hunter@specter.local",
        hashed_password="hashed_argon2_password",
        role="THREAT_HUNTER"
    )
    test_db_session.add(user)
    await test_db_session.commit()

    assert user.id is not None
    assert user.username == "sec_hunter"
    assert user.role == "THREAT_HUNTER"


@pytest.mark.asyncio
async def test_create_normalized_event(test_db_session: AsyncSession):
    event = Event(
        timestamp=datetime.now(timezone.utc),
        source="linux-auth",
        event_type="authentication",
        action="login_failed",
        user_identity="alice",
        host="LAB-PC-01",
        source_ip="10.10.10.50",
        severity="medium",
        raw_event={"msg": "Failed password for alice from 10.10.10.50 port 45222 ssh2"}
    )
    test_db_session.add(event)
    await test_db_session.commit()

    assert event.id.startswith("evt-")
    assert event.action == "login_failed"
    assert event.source_ip == "10.10.10.50"


@pytest.mark.asyncio
async def test_create_entity_and_relationship(test_db_session: AsyncSession):
    user_ent = Entity(id="user:alice", entity_type="USER", value="alice", risk_score=25.0)
    ip_ent = Entity(id="ip:10.10.10.50", entity_type="IP", value="10.10.10.50", risk_score=40.0)

    rel = EntityRelationship(
        id="rel:user:alice-ip:10.10.10.50",
        source_entity_id=user_ent.id,
        target_entity_id=ip_ent.id,
        relation_type="LOGGED_FROM_IP",
        weight=2
    )

    test_db_session.add_all([user_ent, ip_ent, rel])
    await test_db_session.commit()

    assert user_ent.id == "user:alice"
    assert rel.relation_type == "LOGGED_FROM_IP"


@pytest.mark.asyncio
async def test_create_detection_rule_and_alert(test_db_session: AsyncSession):
    rule = DetectionRule(
        id="DET-AUTH-001",
        name="Repeated Failed Authentication",
        severity="high",
        event_type="authentication",
        condition={"action": "login_failed"},
        threshold={"count": 5, "window_minutes": 5},
        group_by=["source_ip", "user"],
        mitre_tactic="Credential Access",
        mitre_technique_id="T1110",
        description="Detects repeated failed authentication attempts."
    )
    test_db_session.add(rule)
    await test_db_session.flush()

    alert = Alert(
        rule_id=rule.id,
        title="Repeated Authentication Failures Detected",
        description="Observed 5 failed logins for user alice from 10.10.10.50",
        severity="high",
        confidence=0.9,
        risk_score=75,
        event_ids=["evt-001", "evt-002", "evt-003", "evt-004", "evt-005"],
        entity_ids=["user:alice", "ip:10.10.10.50"]
    )
    test_db_session.add(alert)
    await test_db_session.commit()

    assert alert.id.startswith("alt-")
    assert alert.rule_id == "DET-AUTH-001"
    assert len(alert.event_ids) == 5


@pytest.mark.asyncio
async def test_create_investigation_and_evidence(test_db_session: AsyncSession):
    inv = Investigation(
        title="Potential Brute Force & Credential Access Investigation",
        status="OPEN",
        priority="HIGH",
        risk_score=75,
        root_entities=["user:alice", "ip:10.10.10.50"]
    )
    test_db_session.add(inv)
    await test_db_session.flush()

    evi = Evidence(
        investigation_id=inv.id,
        evidence_type="log_snippet",
        source="linux-auth-syslog",
        description="Syslog auth failure records",
        content_text="Failed password for alice from 10.10.10.50 port 5532",
        sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        collector_user="analyst1"
    )
    test_db_session.add(evi)
    await test_db_session.commit()

    assert inv.id.startswith("inv-")
    assert evi.id.startswith("evi-")
    assert evi.sha256 is not None
