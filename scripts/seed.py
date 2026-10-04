"""ThreatGraph X - Synthetic Security Telemetry Seeding Script
Generates 20,000 synthetic lab security events, entities, alerts, and investigations.
All data is explicitly labeled: SYNTHETIC LAB DATA.
"""

import asyncio
import random
import uuid
from datetime import datetime, timezone, timedelta
import argparse
import sys
import os
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))
except ImportError:
    pass

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.database.database import AsyncSessionLocal, init_db
from app.models import (
    User, Event, Entity, EntityRelationship, DetectionRule,
    Alert, Investigation, Incident, Evidence, IOC, BehaviorProfile,
    Anomaly, HuntQuery, AuditLog
)
from app.dependencies import hash_password
from app.graph.in_memory_graph import in_memory_graph
from app.services.threat_intel import threat_intel

USERS = ["alice", "bob", "charlie", "david", "eve", "frank", "grace", "heidi", "ivan", "judy", "testuser", "svc_backup", "admin_sec"]
HOSTS = ["LAB-PC-01", "LAB-PC-02", "WORKSTATION-01", "WORKSTATION-02", "PROD-DB-01", "APP-SRV-01", "DC-01", "DC-02", "GATEWAY-01"]
INTERNAL_IPS = [f"10.10.10.{i}" for i in range(10, 150)] + [f"192.168.1.{i}" for i in range(10, 100)]
EXTERNAL_IPS = ["198.51.100.25", "203.0.113.19", "185.220.101.5", "91.240.118.172", "194.26.29.112"]
DOMAINS = ["c2-server.test", "evil-cdn.test", "update-check.test", "corp.internal", "db.internal"]
PROCESSES = ["powershell.exe", "cmd.exe", "whoami.exe", "curl.exe", "7z.exe", "explorer.exe", "svchost.exe", "python.exe", "nginx.exe", "certutil.exe"]
FILES = ["/etc/shadow", "/etc/passwd", "C:\\Windows\\System32\\config\\SAM", "C:\\Users\\alice\\passwords.txt", "C:\\Users\\bob\\Documents\\financials.xlsx", "/var/log/auth.log"]


async def seed_database(target_events_count: int = 20000):
    print(f"[*] Initializing ThreatGraph X Database...")
    await init_db()

    async with AsyncSessionLocal() as session:
        print(f"[*] Seeding Default Users & RBAC Roles...")
        default_users = [
            ("admin", "admin@threatgraph.local", os.environ.get("SEED_ADMIN_PASSWORD", "changeme_admin"), "ADMIN"),
            ("hunter", "hunter@threatgraph.local", os.environ.get("SEED_HUNTER_PASSWORD", "changeme_hunter"), "THREAT_HUNTER"),
            ("analyst", "analyst@threatgraph.local", os.environ.get("SEED_ANALYST_PASSWORD", "changeme_analyst"), "SOC_ANALYST"),
            ("viewer", "viewer@threatgraph.local", os.environ.get("SEED_VIEWER_PASSWORD", "changeme_viewer"), "VIEWER"),
        ]
        for uname, uemail, upass, urole in default_users:
            user = User(
                username=uname,
                email=uemail,
                hashed_password=hash_password(upass),
                role=urole
            )
            session.add(user)
        await session.commit()

        print(f"[*] Seeding Threat Intelligence IOCs...")
        await threat_intel.seed_default_iocs(session)

        print(f"[*] Generating {target_events_count} SYNTHETIC LAB DATA security events...")
        base_time = datetime.now(timezone.utc) - timedelta(days=7)
        batch_size = 1000
        events_batch = []
        now = datetime.now(timezone.utc)

        # Pre-seed Entities in Memory Graph & DB
        entity_cache = set()
        for u in USERS:
            uid = f"user:{u}"
            entity_cache.add(uid)
            in_memory_graph.add_or_update_node(uid, "User", {"name": u})
            session.add(Entity(id=uid, entity_type="USER", value=u, first_seen=base_time, last_seen=now))

        for h in HOSTS:
            hid = f"host:{h}"
            entity_cache.add(hid)
            in_memory_graph.add_or_update_node(hid, "Host", {"hostname": h})
            session.add(Entity(id=hid, entity_type="HOST", value=h, first_seen=base_time, last_seen=now))

        for ip in INTERNAL_IPS[:50] + EXTERNAL_IPS:
            ipid = f"ip:{ip}"
            entity_cache.add(ipid)
            in_memory_graph.add_or_update_node(ipid, "IP", {"address": ip})
            session.add(Entity(id=ipid, entity_type="IP", value=ip, first_seen=base_time, last_seen=now))

        await session.commit()

        event_actions = [
            ("authentication", "login_success", "low"),
            ("authentication", "login_failed", "medium"),
            ("process", "process_created", "low"),
            ("process", "process_terminated", "informational"),
            ("network", "outbound_connection", "low"),
            ("network", "dns_query", "informational"),
            ("file", "file_read", "informational"),
            ("file", "sensitive_access", "high"),
            ("privilege", "privilege_change", "high")
        ]

        total_created = 0
        for i in range(target_events_count):
            ev_type, action, sev = random.choice(event_actions)
            user = random.choice(USERS)
            host = random.choice(HOSTS)
            src_ip = random.choice(INTERNAL_IPS)
            dst_ip = random.choice(EXTERNAL_IPS if random.random() < 0.2 else INTERNAL_IPS)
            proc = random.choice(PROCESSES)
            fpath = random.choice(FILES) if ev_type == "file" else None
            ev_time = base_time + timedelta(seconds=random.randint(0, 7 * 86400))

            ev = Event(
                id=f"evt-synth-{uuid.uuid4().hex[:10]}",
                timestamp=ev_time,
                source=random.choice(["linux-auth", "sysmon", "zeek", "auditd", "cloudtrail"]),
                event_type=ev_type,
                action=action,
                user_identity=user,
                host=host,
                source_ip=src_ip,
                destination_ip=dst_ip if ev_type == "network" else None,
                domain=random.choice(DOMAINS) if ev_type == "network" else None,
                process_name=proc if ev_type == "process" else None,
                parent_process="cmd.exe" if ev_type == "process" and random.random() < 0.3 else None,
                file_path=fpath,
                severity=sev,
                raw_event={"synthetic": True, "label": "SYNTHETIC LAB DATA", "sim_idx": i},
                metadata_json={"environment": "lab", "dataset": "synthetic-20k"}
            )
            events_batch.append(ev)

            # Link in in-memory graph
            in_memory_graph.add_or_update_edge(f"user:{user}", f"host:{host}", "ACCESSED_HOST")
            in_memory_graph.add_or_update_edge(f"host:{host}", f"proc:{host}:{proc}", "EXECUTED_PROCESS")
            if ev_type == "network":
                in_memory_graph.add_or_update_edge(f"host:{host}", f"ip:{dst_ip}", "CONNECTED_TO_IP")

            if len(events_batch) >= batch_size:
                session.add_all(events_batch)
                await session.commit()
                total_created += len(events_batch)
                print(f"    -> Ingested {total_created}/{target_events_count} events...")
                events_batch = []

        if events_batch:
            session.add_all(events_batch)
            await session.commit()
            total_created += len(events_batch)

        print(f"[*] Creating Baseline Alerts & Investigations...")
        # Create sample alerts
        alert1 = Alert(
            id="alt-seed-001",
            rule_id="DET-AUTH-001",
            title="Repeated Failed Authentication Observed",
            description="SYNTHETIC LAB DATA: 5 failed logins detected against user testuser.",
            severity="high",
            confidence=0.88,
            risk_score=75,
            status="NEW",
            event_ids=["evt-seed-1", "evt-seed-2"],
            entity_ids=["user:testuser", "ip:198.51.100.25"],
            mitre_tactic="Credential Access",
            mitre_technique="T1110 Brute Force",
            first_seen=base_time,
            last_seen=now
        )
        alert2 = Alert(
            id="alt-seed-002",
            rule_id="DET-EXEC-001",
            title="Suspicious Process Execution",
            description="SYNTHETIC LAB DATA: PowerShell invoked by testuser on LAB-PC-01.",
            severity="high",
            confidence=0.90,
            risk_score=80,
            status="INVESTIGATING",
            event_ids=["evt-seed-3"],
            entity_ids=["user:testuser", "host:LAB-PC-01"],
            mitre_tactic="Execution",
            mitre_technique="T1059 Command and Scripting Interpreter",
            first_seen=base_time,
            last_seen=now
        )
        session.add_all([alert1, alert2])

        # Sample Investigation
        inv = Investigation(
            id="inv-seed-001",
            title="Correlated Multi-Stage Lateral Movement Investigation",
            status="OPEN",
            priority="CRITICAL",
            summary="SYNTHETIC LAB DATA: Multi-stage intrusion trace spanning credential access to internal network connection.",
            confidence=0.92,
            risk_score=88,
            root_entities=["user:testuser", "host:LAB-PC-01", "ip:198.51.100.25"],
            related_alerts=["alt-seed-001", "alt-seed-002"],
            mitre_tactics=["Credential Access", "Execution", "Collection"]
        )
        session.add(inv)

        # Sample Saved Hunt
        hunt = HuntQuery(
            name="External Inbound SSH Anomaly Hunt",
            description="Proactively searches for off-subnet authentication attempts",
            query_dsl={"field": "source_ip", "op": "CONTAINS", "value": "198.51."},
            raw_query='source_ip CONTAINS "198.51." AND severity >= "medium"'
        )
        session.add(hunt)

        await session.commit()
        stats = in_memory_graph.get_stats()
        print(f"\n========================================================")
        print(f" ThreatGraph X Synthetic Lab Database Seeded Successfully!")
        print(f" Total Events:        {total_created}")
        print(f" Graph Nodes:         {stats['node_count']}")
        print(f" Graph Relationships: {stats['edge_count']}")
        print(f" Notice:              ALL DATA LABELED SYNTHETIC LAB DATA")
        print(f"========================================================\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed ThreatGraph X Database")
    parser.add_argument("--events", type=int, default=20000, help="Total synthetic events to generate")
    args = parser.parse_args()
    asyncio.run(seed_database(args.events))
