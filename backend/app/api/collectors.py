from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from pydantic import BaseModel

from app.database.database import get_db
from app.services.live_collector import live_collector
from app.schemas.event import NormalizedEventResponse

router = APIRouter(prefix="/collectors", tags=["Log Collectors & Ingestion"])


class SyslogIngestRequest(BaseModel):
    raw_messages: List[str]
    source_tag: str = "firewall-syslog"


class WebhookEventIngest(BaseModel):
    source: str = "CloudTrail/Okta"
    payload: Dict[str, Any]


@router.post("/syslog", status_code=status.HTTP_201_CREATED)
async def ingest_syslog_stream(
    req: SyslogIngestRequest,
    db: AsyncSession = Depends(get_db)
):
    """Parses RFC 5424 / RFC 3164 Syslog messages, extracts entities, and correlates into graph."""
    ingested = []
    alerts_triggered = 0

    for line in req.raw_messages:
        parsed = live_collector.parse_syslog_line(line)
        ev, alerts = await live_collector.ingest_normalized_event(db, parsed)
        ingested.append(ev.id)
        alerts_triggered += len(alerts)

    return {
        "status": "success",
        "messages_received": len(req.raw_messages),
        "events_created": len(ingested),
        "alerts_triggered": alerts_triggered,
        "event_ids": ingested
    }


@router.post("/windows-event", status_code=status.HTTP_201_CREATED)
async def ingest_windows_event(
    events: List[Dict[str, Any]] = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """Ingests Windows Security & Sysmon structured event records."""
    ingested = []
    alerts_triggered = 0

    for raw_ev in events:
        parsed = live_collector.parse_windows_event(raw_ev)
        ev, alerts = await live_collector.ingest_normalized_event(db, parsed)
        ingested.append(ev.id)
        alerts_triggered += len(alerts)

    return {
        "status": "success",
        "windows_events_processed": len(events),
        "events_created": len(ingested),
        "alerts_triggered": alerts_triggered,
        "event_ids": ingested
    }


@router.post("/webhook", status_code=status.HTTP_201_CREATED)
async def ingest_cloud_webhook(
    req: WebhookEventIngest,
    db: AsyncSession = Depends(get_db)
):
    """Ingests CloudTrail, Okta, GitHub, or generic security webhook telemetry."""
    # Normalize generic payload
    payload = req.payload
    parsed = {
        "event_type": payload.get("event_type", "network"),
        "action": payload.get("action", "cloud_api_call"),
        "source_ip": payload.get("source_ip") or payload.get("sourceIPAddress"),
        "dest_ip": payload.get("dest_ip") or payload.get("destinationIPAddress"),
        "host": payload.get("host") or payload.get("awsRegion", "CLOUD-VPC"),
        "user": payload.get("user") or payload.get("userIdentity", {}).get("userName"),
        "process": payload.get("process") or payload.get("eventName"),
        "command_line": payload.get("command_line"),
        "raw_log": str(payload)
    }
    ev, alerts = await live_collector.ingest_normalized_event(db, parsed)
    return {
        "status": "success",
        "event_id": ev.id,
        "alerts_triggered": len(alerts)
    }


@router.get("/stats")
async def get_collector_stats():
    """Returns active collector telemetry stats and supported formats."""
    return {
        "active_collectors": [
            {"type": "Syslog RFC 5424/3164", "status": "ACTIVE", "endpoint": "/api/collectors/syslog"},
            {"type": "Windows Event / Sysmon", "status": "ACTIVE", "endpoint": "/api/collectors/windows-event"},
            {"type": "CloudTrail / Auth Webhooks", "status": "ACTIVE", "endpoint": "/api/collectors/webhook"}
        ],
        "supported_codecs": ["RFC5424", "RFC3164", "Sysmon_v14", "AWS_CloudTrail_JSON", "Okta_SystemLog"]
    }
