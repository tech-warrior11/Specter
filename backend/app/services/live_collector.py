import re
import json
import uuid
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.schemas.event import EventCreate
from app.services.ingestion import ingestion_service
from app.services.detection import detection_engine
from app.models.event import Event

logger = logging.getLogger("specter.services.collector")

# Syslog RFC 5424 and 3164 regex patterns
RFC5424_PATTERN = re.compile(
    r"^<(?P<pri>\d+)>(?P<ver>\d+)\s+(?P<time>\S+)\s+(?P<host>\S+)\s+(?P<app>\S+)\s+(?P<pid>\S+)\s+(?P<msgid>\S+)\s+(?P<sd>.*?)\s+(?P<msg>.*)$"
)
RFC3164_PATTERN = re.compile(
    r"^<(?P<pri>\d+)>(?P<time>[A-Za-z]{3}\s+\d+\s+\d+:\d+:\d+)\s+(?P<host>\S+)\s+(?P<app>[^:\[]+)(?:\[(?P<pid>\d+)\])?:\s*(?P<msg>.*)$"
)


class LiveLogCollectorService:
    """Enterprise Log Ingestion and Normalization Engine for Syslog, Windows Events, and Cloud Webhooks."""

    @staticmethod
    def parse_syslog_line(raw_line: str) -> Dict[str, Any]:
        raw_line = raw_line.strip()
        host = "UNKNOWN-HOST"
        app = "syslog"
        msg = raw_line
        event_type = "network"
        action = "syslog_message"
        user = None
        src_ip = None
        dst_ip = None
        process = None

        # 1. Match RFC 5424
        m5424 = RFC5424_PATTERN.match(raw_line)
        if m5424:
            d = m5424.groupdict()
            host = d.get("host") or host
            app = d.get("app") or app
            msg = d.get("msg") or msg
        else:
            # 2. Match RFC 3164
            m3164 = RFC3164_PATTERN.match(raw_line)
            if m3164:
                d = m3164.groupdict()
                host = d.get("host") or host
                app = d.get("app") or app
                msg = d.get("msg") or msg

        # Extract IPs from message
        ip_matches = re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", raw_line)
        if len(ip_matches) >= 2:
            src_ip, dst_ip = ip_matches[0], ip_matches[1]
        elif len(ip_matches) == 1:
            src_ip = ip_matches[0]

        # Classify semantics
        msg_lower = msg.lower()
        if "failed password" in msg_lower or "authentication failure" in msg_lower or "login failed" in msg_lower:
            event_type = "authentication"
            action = "failed_login"
            user_m = re.search(r"for (?:invalid user )?(\w+)", msg, re.IGNORECASE)
            if user_m:
                user = user_m.group(1)
        elif "accepted password" in msg_lower or "session opened" in msg_lower or "successful login" in msg_lower:
            event_type = "authentication"
            action = "successful_login"
            user_m = re.search(r"for (\w+)", msg, re.IGNORECASE)
            if user_m:
                user = user_m.group(1)
        elif "sudo:" in msg_lower or "privilege" in msg_lower or "elevation" in msg_lower:
            event_type = "privilege"
            action = "privilege_escalation"
        elif "process" in msg_lower or "exec" in msg_lower or ".exe" in msg_lower or "powershell" in msg_lower:
            event_type = "execution"
            action = "process_spawn"
            proc_m = re.search(r"(\b[\w-]+\.(?:exe|sh|bin|py|ps1)\b)", msg, re.IGNORECASE)
            if proc_m:
                process = proc_m.group(1)

        return {
            "source": f"syslog-{app}",
            "event_type": event_type,
            "action": action,
            "source_ip": src_ip,
            "destination_ip": dst_ip,
            "host": host,
            "user": user,
            "process": process or app,
            "raw_event": {"raw_log": raw_line}
        }

    @staticmethod
    def parse_windows_event(event_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Parses Windows Security Event Log / Sysmon JSON format."""
        event_id = event_dict.get("EventID") or event_dict.get("event_id") or 0
        data = event_dict.get("EventData") or event_dict.get("data") or {}

        host = event_dict.get("Computer") or data.get("ComputerName") or "WIN-ENDPOINT-01"
        user = data.get("TargetUserName") or data.get("SubjectUserName") or data.get("User")
        src_ip = data.get("IpAddress") or data.get("SourceIp")
        process = data.get("Image") or data.get("ProcessName") or data.get("OriginalFileName")
        dest_ip = data.get("DestinationIp")

        event_type = "execution"
        action = "process_creation"

        if event_id in [4624, "4624"]:
            event_type = "authentication"
            action = "successful_login"
        elif event_id in [4625, "4625"]:
            event_type = "authentication"
            action = "failed_login"
        elif event_id in [4672, "4672"]:
            event_type = "privilege"
            action = "special_privileges_assigned"
        elif event_id in [3, "3"]:  # Sysmon Network Connect
            event_type = "network"
            action = "outbound_connection"
        elif event_id in [1, "1"]:  # Sysmon Process Create
            event_type = "execution"
            action = "process_spawn"

        return {
            "source": "windows-security-sysmon",
            "event_type": event_type,
            "action": action,
            "source_ip": src_ip,
            "destination_ip": dest_ip,
            "host": host,
            "user": user,
            "process": process,
            "raw_event": event_dict
        }

    @staticmethod
    async def ingest_normalized_event(session: AsyncSession, event_payload: Dict[str, Any]) -> Tuple[Event, List[Any]]:
        event_in = EventCreate(**event_payload)
        norm_ev, _, _ = await ingestion_service.ingest_event(session, event_in)
        alerts = await detection_engine.evaluate_event(session, norm_ev)
        return norm_ev, alerts


live_collector = LiveLogCollectorService()

