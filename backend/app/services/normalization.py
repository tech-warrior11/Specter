from datetime import datetime, timezone
from typing import Dict, Any, Optional
import uuid
import logging
from app.schemas.event import EventCreate
from app.models.event import Event

logger = logging.getLogger("specter.normalization")


class NormalizationEngine:
    """Normalizes disparate log sources into standardized ECS/OCSF compliant event taxonomy."""

    @staticmethod
    def normalize(event_in: EventCreate) -> Event:
        # Determine timestamp
        event_time = event_in.timestamp or datetime.now(timezone.utc)
        if event_time.tzinfo is None:
            event_time = event_time.replace(tzinfo=timezone.utc)

        # Standardize Event ID
        event_id = event_in.event_id or f"evt-{uuid.uuid4().hex[:12]}"
        if not event_id.startswith("evt-"):
            event_id = f"evt-{event_id}"

        # Standardize Strings
        user_identity = event_in.user.strip().lower() if event_in.user else None
        host = event_in.host.strip().upper() if event_in.host else None
        source_ip = event_in.source_ip.strip() if event_in.source_ip else None
        destination_ip = event_in.destination_ip.strip() if event_in.destination_ip else None
        domain = event_in.domain.strip().lower() if event_in.domain else None
        process_name = event_in.process.strip().lower() if event_in.process else None
        parent_process = event_in.parent_process.strip().lower() if event_in.parent_process else None
        file_path = event_in.file_path.strip() if event_in.file_path else None
        file_hash = event_in.hash.strip().lower() if event_in.hash else None
        resource_id = event_in.resource.strip() if event_in.resource else None

        # Severity standardizer
        sev = event_in.severity.lower()
        if sev not in ["informational", "low", "medium", "high", "critical"]:
            sev = "informational"

        raw = event_in.raw_event or {}
        if not raw:
            raw = {
                "source": event_in.source,
                "event_type": event_in.event_type,
                "action": event_in.action,
                "user": user_identity,
                "host": host,
                "source_ip": source_ip,
                "destination_ip": destination_ip,
                "process": process_name,
                "file_path": file_path
            }

        return Event(
            id=event_id,
            timestamp=event_time,
            source=event_in.source.lower().strip(),
            event_type=event_in.event_type.lower().strip(),
            action=event_in.action.lower().strip(),
            user_identity=user_identity,
            host=host,
            source_ip=source_ip,
            destination_ip=destination_ip,
            domain=domain,
            url=event_in.url,
            process_name=process_name,
            parent_process=parent_process,
            file_path=file_path,
            file_hash=file_hash,
            resource_id=resource_id,
            severity=sev,
            raw_event=raw,
            metadata_json=event_in.metadata or {}
        )


normalization_engine = NormalizationEngine()
