from datetime import datetime, timezone
from app.models.event import Event
from app.services.entity_extractor import entity_extractor


def test_extract_entities_from_multi_attribute_event():
    event = Event(
        id="evt-test-101",
        timestamp=datetime.now(timezone.utc),
        source="sysmon",
        event_type="network",
        action="outbound_connection",
        user_identity="alice",
        host="LAB-PC-01",
        source_ip="10.10.10.50",
        destination_ip="198.51.100.25",
        domain="c2-server.test",
        process_name="powershell.exe",
        parent_process="cmd.exe",
        file_path="C:\\Users\\alice\\mal.ps1",
        file_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        resource_id="res:bucket-confidential",
        severity="high",
        raw_event={}
    )

    entities = entity_extractor.extract_entities(event)
    ent_ids = [e.id for e in entities]

    assert "user:alice" in ent_ids
    assert "host:LAB-PC-01" in ent_ids
    assert "ip:10.10.10.50" in ent_ids
    assert "ip:198.51.100.25" in ent_ids
    assert "domain:c2-server.test" in ent_ids
    assert "proc:LAB-PC-01:powershell.exe" in ent_ids
    assert "proc:LAB-PC-01:cmd.exe" in ent_ids
    assert "file:C:\\Users\\alice\\mal.ps1" in ent_ids
    assert "hash:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" in ent_ids
    assert "res:bucket-confidential" in ent_ids


def test_extract_relationships_from_event():
    event = Event(
        id="evt-test-102",
        timestamp=datetime.now(timezone.utc),
        source="linux-auth",
        event_type="authentication",
        action="login_success",
        user_identity="bob",
        host="PROD-DB-01",
        source_ip="10.10.20.100",
        severity="low",
        raw_event={}
    )

    rels = entity_extractor.extract_relationships(event)
    rel_types = [r[2] for r in rels]

    assert "LOGGED_FROM_IP" in rel_types
    assert "ACCESSED_HOST" in rel_types
