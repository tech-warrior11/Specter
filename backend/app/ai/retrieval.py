from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.investigation import Investigation
from app.models.event import Event
from app.models.alert import Alert
from app.models.evidence import Evidence


class EvidenceRetrievalEngine:
    """Retrieves grounded security context strictly bounded by active investigation data."""

    @staticmethod
    async def retrieve_context(session: AsyncSession, investigation_id: str) -> Dict[str, Any]:
        inv = await session.get(Investigation, investigation_id)
        if not inv:
            return {"error": f"Investigation {investigation_id} not found", "available": False}

        # Fetch Events
        events = []
        if inv.related_events:
            ev_stmt = select(Event).where(Event.id.in_(inv.related_events))
            ev_res = await session.execute(ev_stmt)
            for e in ev_res.scalars().all():
                events.append({
                    "id": e.id,
                    "timestamp": e.timestamp.isoformat(),
                    "action": e.action,
                    "user": e.user_identity,
                    "host": e.host,
                    "source_ip": e.source_ip,
                    "destination_ip": e.destination_ip,
                    "process": e.process_name,
                    "file": e.file_path,
                    "severity": e.severity
                })

        # Fetch Alerts
        alerts = []
        if inv.related_alerts:
            alt_stmt = select(Alert).where(Alert.id.in_(inv.related_alerts))
            alt_res = await session.execute(alt_stmt)
            for a in alt_res.scalars().all():
                alerts.append({
                    "id": a.id,
                    "rule_id": a.rule_id,
                    "title": a.title,
                    "severity": a.severity,
                    "mitre_tactic": a.mitre_tactic,
                    "mitre_technique": a.mitre_technique
                })

        # Fetch Evidence
        evidence = []
        evi_stmt = select(Evidence).where(Evidence.investigation_id == investigation_id)
        evi_res = await session.execute(evi_stmt)
        for evi in evi_res.scalars().all():
            evidence.append({
                "id": evi.id,
                "type": evi.evidence_type,
                "description": evi.description,
                "sha256": evi.sha256
            })

        return {
            "investigation_id": inv.id,
            "title": inv.title,
            "root_entities": inv.root_entities or [],
            "mitre_tactics": inv.mitre_tactics or [],
            "events": events,
            "alerts": alerts,
            "evidence": evidence,
            "available": True
        }


retrieval_engine = EvidenceRetrievalEngine()
