import os
import fnmatch
import yaml
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

from app.models.detection_rule import DetectionRule
from app.models.alert import Alert
from app.models.event import Event

logger = logging.getLogger("specter.services.detection")


class DetectionEngine:
    """Evaluates declarative YAML detection rules against security telemetry."""

    def __init__(self):
        self.rules: Dict[str, Dict[str, Any]] = {}
        self.recent_events_buffer: List[Event] = []

    def load_rules_from_disk(self, rules_dir: str):
        """Discovers and parses all YAML detection rule files."""
        count = 0
        for root, _, files in os.walk(rules_dir):
            for file in files:
                if file.endswith((".yaml", ".yml")):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            rule_data = yaml.safe_load(f)
                            if rule_data and "id" in rule_data:
                                self.rules[rule_data["id"]] = rule_data
                                count += 1
                    except Exception as e:
                        logger.error(f"Error loading rule file {filepath}: {e}")
        logger.info(f"Loaded {count} detection rules into memory engine.")

    async def sync_rules_to_db(self, session: AsyncSession):
        """Synchronizes in-memory rules with PostgreSQL database table."""
        for rule_id, r in self.rules.items():
            existing = await session.get(DetectionRule, rule_id)
            if not existing:
                mitre_data = r.get("mitre", {})
                db_rule = DetectionRule(
                    id=rule_id,
                    name=r.get("name", rule_id),
                    severity=r.get("severity", "medium").lower(),
                    event_type=r.get("event_type", "unknown"),
                    condition=r.get("condition", {}),
                    threshold=r.get("threshold", {}),
                    group_by=r.get("group_by", []),
                    mitre_tactic=mitre_data.get("tactic"),
                    mitre_technique_id=mitre_data.get("technique_id"),
                    mitre_technique_name=mitre_data.get("technique_name"),
                    description=r.get("description", ""),
                    enabled=True
                )
                session.add(db_rule)
        await session.commit()

    def _event_matches_condition(self, event: Event, cond: Dict[str, Any], rule_etype: str) -> bool:
        # Check event_type
        if rule_etype != "multi-stage" and rule_etype != event.event_type:
            return False

        # Check action
        req_action = cond.get("action")
        if req_action:
            if isinstance(req_action, list) and event.action not in req_action:
                return False
            elif isinstance(req_action, str) and event.action != req_action:
                return False

        # Check process
        if "process" in cond:
            req_procs = cond["process"]
            if isinstance(req_procs, list):
                if not event.process_name or event.process_name not in [p.lower() for p in req_procs]:
                    return False
            elif isinstance(req_procs, str):
                if not event.process_name or event.process_name != req_procs.lower():
                    return False

        # Check parent_process
        if "parent_process" in cond:
            req_parents = cond["parent_process"]
            if isinstance(req_parents, list):
                if not event.parent_process or event.parent_process not in [p.lower() for p in req_parents]:
                    return False
            elif isinstance(req_parents, str):
                if not event.parent_process or event.parent_process != req_parents.lower():
                    return False

        # Check file_patterns
        if "file_patterns" in cond:
            patterns = cond["file_patterns"]
            if not event.file_path:
                return False
            matched_pattern = False
            for pat in patterns:
                if fnmatch.fnmatch(event.file_path.lower(), pat.lower()):
                    matched_pattern = True
                    break
            if not matched_pattern:
                return False

        # Check keywords
        if "keywords" in cond:
            keywords = cond["keywords"]
            raw_str = str(event.raw_event).lower() + " " + str(event.process_name or "").lower()
            if not any(kw.lower() in raw_str for kw in keywords):
                return False

        return True

    async def evaluate_event(self, session: AsyncSession, event: Event) -> List[Alert]:
        """Evaluates all enabled detection rules against an incoming event."""
        self.recent_events_buffer.append(event)
        if len(self.recent_events_buffer) > 1000:
            self.recent_events_buffer = self.recent_events_buffer[-1000:]

        generated_alerts: List[Alert] = []

        for rule_id, rule in self.rules.items():
            cond = rule.get("condition", {})
            thresh = rule.get("threshold", {"count": 1, "window_minutes": 5})
            req_count = thresh.get("count", 1)
            window_mins = thresh.get("window_minutes", 5)
            rule_etype = rule.get("event_type", "")

            # Check if current event matches condition
            if not self._event_matches_condition(event, cond, rule_etype):
                continue

            # Ensure event timestamp is timezone aware
            ev_time = event.timestamp
            if ev_time.tzinfo is None:
                ev_time = ev_time.replace(tzinfo=timezone.utc)

            cutoff_time = ev_time - timedelta(minutes=window_mins)

            matching_events = []
            for e in self.recent_events_buffer:
                e_time = e.timestamp
                if e_time.tzinfo is None:
                    e_time = e_time.replace(tzinfo=timezone.utc)

                if e_time >= cutoff_time and self._event_matches_condition(e, cond, rule_etype):
                    matching_events.append(e)

            # Group By Matching
            group_keys = rule.get("group_by", [])
            filtered_matches = []
            for e in matching_events:
                matches_group = True
                for gk in group_keys:
                    if gk == "source_ip" and e.source_ip != event.source_ip:
                        matches_group = False
                    elif gk == "user" and e.user_identity != event.user_identity:
                        matches_group = False
                    elif gk == "host" and e.host != event.host:
                        matches_group = False
                if matches_group:
                    filtered_matches.append(e)

            if len(filtered_matches) >= req_count:
                mitre_info = rule.get("mitre", {})
                ent_ids = []
                if event.user_identity:
                    ent_ids.append(f"user:{event.user_identity}")
                if event.host:
                    ent_ids.append(f"host:{event.host}")
                if event.source_ip:
                    ent_ids.append(f"ip:{event.source_ip}")

                alert = Alert(
                    rule_id=rule_id,
                    title=f"Alert: {rule.get('name', rule_id)}",
                    description=f"Observed activity consistent with {rule.get('name')}. Triggered on {len(filtered_matches)} events.",
                    severity=rule.get("severity", "medium").lower(),
                    confidence=0.85,
                    risk_score=80 if rule.get("severity") == "critical" else (65 if rule.get("severity") == "high" else 45),
                    status="NEW",
                    event_ids=[e.id for e in filtered_matches],
                    entity_ids=list(set(ent_ids)),
                    mitre_tactic=mitre_info.get("tactic"),
                    mitre_technique=f"{mitre_info.get('technique_id', '')} {mitre_info.get('technique_name', '')}".strip(),
                    first_seen=filtered_matches[0].timestamp,
                    last_seen=filtered_matches[-1].timestamp
                )
                session.add(alert)

                db_rule = await session.get(DetectionRule, rule_id)
                if db_rule:
                    db_rule.trigger_count += 1

                generated_alerts.append(alert)

        if generated_alerts:
            await session.commit()

        return generated_alerts


detection_engine = DetectionEngine()
rules_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "detection-rules"))
if os.path.exists(rules_path):
    detection_engine.load_rules_from_disk(rules_path)
