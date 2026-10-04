from datetime import datetime, timezone
from app.schemas.event import EventCreate
from app.services.normalization import normalization_engine


def test_normalize_authentication_event():
    event_in = EventCreate(
        source="Linux-Auth-Syslog",
        event_type="Authentication",
        action="LOGIN_FAILED",
        user="Alice",
        host="lab-pc-01",
        source_ip="10.10.10.50",
        severity="HIGH"
    )
    normalized = normalization_engine.normalize(event_in)

    assert normalized.id.startswith("evt-")
    assert normalized.source == "linux-auth-syslog"
    assert normalized.event_type == "authentication"
    assert normalized.action == "login_failed"
    assert normalized.user_identity == "alice"
    assert normalized.host == "LAB-PC-01"
    assert normalized.source_ip == "10.10.10.50"
    assert normalized.severity == "high"
    assert normalized.timestamp.tzinfo is not None


def test_normalize_process_event():
    event_in = EventCreate(
        source="Sysmon",
        event_type="process",
        action="process_created",
        user="SYSTEM",
        host="DC-01",
        process="powershell.exe",
        parent_process="cmd.exe",
        severity="medium"
    )
    normalized = normalization_engine.normalize(event_in)

    assert normalized.process_name == "powershell.exe"
    assert normalized.parent_process == "cmd.exe"
    assert normalized.host == "DC-01"
