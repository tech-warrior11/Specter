import os
import yaml
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.schemas.event import EventCreate
from app.services.ingestion import ingestion_service
from app.services.detection import detection_engine
from app.services.correlation import correlation_engine
from app.services.investigation import investigation_service
from app.services.risk import risk_engine
from app.models.investigation import Investigation

logger = logging.getLogger("specter.services.scenario_runner")


class ScenarioRunner:
    """Manages and executes controlled synthetic attack-chain scenarios."""

    def __init__(self):
        self.scenarios_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "scenarios"))

    def list_scenarios(self) -> List[Dict[str, Any]]:
        scenarios = []
        if not os.path.exists(self.scenarios_dir):
            return scenarios

        for file in os.listdir(self.scenarios_dir):
            if file.endswith((".yaml", ".yml")):
                fpath = os.path.join(self.scenarios_dir, file)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f)
                        if data and "id" in data:
                            scenarios.append({
                                "id": data["id"],
                                "name": data.get("name", file),
                                "description": data.get("description", ""),
                                "event_count": len(data.get("events", [])),
                                "expected_detections": data.get("expected_detections", []),
                                "filename": file
                            })
                except Exception as e:
                    logger.error(f"Error loading scenario {file}: {e}")
        return scenarios

    async def run_scenario(self, session: AsyncSession, scenario_id_or_file: str) -> Dict[str, Any]:
        """Executes a scenario and returns end-to-end security correlation results."""
        scenario_data = None
        for file in os.listdir(self.scenarios_dir):
            if file.endswith((".yaml", ".yml")):
                fpath = os.path.join(self.scenarios_dir, file)
                with open(fpath, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    if data and (data.get("id") == scenario_id_or_file or file.startswith(scenario_id_or_file)):
                        scenario_data = data
                        break

        if not scenario_data:
            raise ValueError(f"Scenario '{scenario_id_or_file}' not found.")

        events_raw = scenario_data.get("events", [])
        ingested_events = []
        triggered_alerts = []

        # 1. Ingest events & evaluate detections
        for ev in events_raw:
            event_create = EventCreate(**ev)
            norm_event, _, _ = await ingestion_service.ingest_event(session, event_create)
            ingested_events.append(norm_event)

            # Evaluate detection rules
            alerts = await detection_engine.evaluate_event(session, norm_event)
            triggered_alerts.extend(alerts)

        # 2. Correlate Alerts & Generate Investigation
        primary_entity = f"user:{ingested_events[0].user_identity}" if ingested_events and ingested_events[0].user_identity else "user:testuser"
        investigation = await correlation_engine.correlate_entity_alerts(session, primary_entity)

        # 3. Calculate Risk
        risk_result = risk_engine.calculate_risk(
            severity="critical" if len(triggered_alerts) >= 3 else "high",
            confidence=0.88,
            entity_criticality="high",
            attack_chain_depth=min(5, len(triggered_alerts) + 1)
        )

        # 4. Generate Security Story
        story = investigation_service.generate_security_story(ingested_events, triggered_alerts)

        return {
            "scenario_id": scenario_data.get("id"),
            "scenario_name": scenario_data.get("name"),
            "events_generated_count": len(ingested_events),
            "alerts_triggered_count": len(triggered_alerts),
            "alerts": [
                {
                    "id": a.id,
                    "rule_id": a.rule_id,
                    "title": a.title,
                    "severity": a.severity,
                    "mitre_tactic": a.mitre_tactic
                }
                for a in triggered_alerts
            ],
            "investigation_id": investigation.id if investigation else None,
            "risk_assessment": risk_result,
            "security_story": story,
            "status": "COMPLETED_SUCCESSFULLY"
        }


scenario_runner = ScenarioRunner()
