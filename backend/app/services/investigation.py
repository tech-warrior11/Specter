import hashlib
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
import logging

from app.models.investigation import Investigation, InvestigationNote
from app.models.evidence import Evidence
from app.models.event import Event
from app.models.alert import Alert
from app.schemas.investigation import (
    InvestigationWorkbenchResponse,
    InvestigationCreate,
    InvestigationNoteCreate,
    EvidenceCreate,
    EvidenceResponse,
    InvestigationNoteResponse
)
from app.graph.in_memory_graph import in_memory_graph
from app.graph.graph_algorithms import graph_algorithms
from app.services.timeline import timeline_engine

logger = logging.getLogger("specter.services.investigation")


class InvestigationService:
    """Core investigation workbench, evidence vault, and security story generator."""

    @staticmethod
    def generate_security_story(events: List[Event], alerts: List[Alert]) -> str:
        """Deterministically generates a structured, evidence-grounded investigation narrative."""
        if not events and not alerts:
            return "Insufficient telemetry data available in the current investigation."

        story_steps = []
        ev_refs = []

        # Sort events chronologically
        sorted_events = sorted(events, key=lambda e: e.timestamp)

        step_num = 1
        for ev in sorted_events:
            ev_refs.append(ev.id)
            if ev.event_type == "authentication":
                if ev.action == "login_failed":
                    story_steps.append(f"{step_num}. An authentication failure was recorded for user '{ev.user_identity}' from source IP '{ev.source_ip}'.")
                elif ev.action == "login_success":
                    story_steps.append(f"{step_num}. A successful authentication was subsequently observed for user '{ev.user_identity}' accessing host '{ev.host}'.")
                else:
                    story_steps.append(f"{step_num}. Authentication activity '{ev.action}' occurred on host '{ev.host}'.")
            elif ev.event_type == "process":
                story_steps.append(f"{step_num}. A process execution event ('{ev.process_name}') was observed on endpoint '{ev.host}'.")
            elif ev.event_type == "privilege":
                story_steps.append(f"{step_num}. Account privilege token modification was detected for user '{ev.user_identity}' on '{ev.host}'.")
            elif ev.event_type == "file":
                story_steps.append(f"{step_num}. File system interaction was observed against file '{ev.file_path}'.")
            elif ev.event_type == "network":
                story_steps.append(f"{step_num}. Network egress was established from host '{ev.host}' to destination '{ev.destination_ip or ev.domain}'.")
            else:
                story_steps.append(f"{step_num}. Telemetry event '{ev.action}' was recorded on '{ev.host}'.")
            step_num += 1

        story_text = "\n".join(story_steps)
        evidence_text = f"\n\nSupporting Forensic Evidence References:\n- " + "\n- ".join(ev_refs[:15])

        return f"### Security Investigation Narrative\n\n{story_text}{evidence_text}"

    @staticmethod
    async def get_workbench(session: AsyncSession, investigation_id: str) -> InvestigationWorkbenchResponse:
        inv = await session.get(Investigation, investigation_id)
        if not inv:
            raise ValueError(f"Investigation {investigation_id} not found")

        # Fetch Events
        ev_list: List[Event] = []
        if inv.related_events:
            ev_stmt = select(Event).where(Event.id.in_(inv.related_events))
            ev_res = await session.execute(ev_stmt)
            ev_list = ev_res.scalars().all()

        # Fetch Alerts
        alt_list: List[Alert] = []
        if inv.related_alerts:
            alt_stmt = select(Alert).where(Alert.id.in_(inv.related_alerts))
            alt_res = await session.execute(alt_stmt)
            alt_list = alt_res.scalars().all()

        # Fetch Notes
        note_stmt = select(InvestigationNote).where(InvestigationNote.investigation_id == investigation_id).order_by(InvestigationNote.created_at)
        note_res = await session.execute(note_stmt)
        notes = [
            InvestigationNoteResponse(
                id=n.id,
                investigation_id=n.investigation_id,
                author_id=n.author_id,
                content=n.content,
                related_entity_id=n.related_entity_id,
                related_event_id=n.related_event_id,
                created_at=n.created_at
            )
            for n in note_res.scalars().all()
        ]

        # Fetch Evidence
        evi_stmt = select(Evidence).where(Evidence.investigation_id == investigation_id).order_by(Evidence.collected_at)
        evi_res = await session.execute(evi_stmt)
        evidence = [
            EvidenceResponse(
                id=e.id,
                investigation_id=e.investigation_id,
                evidence_type=e.evidence_type,
                source=e.source,
                description=e.description,
                content_text=e.content_text,
                sha256=e.sha256,
                size_bytes=e.size_bytes or 0,
                collector_user=e.collector_user,
                collected_at=e.collected_at
            )
            for e in evi_res.scalars().all()
        ]

        # Build Timeline
        timeline = await timeline_engine.build_timeline(
            session=session,
            event_ids=inv.related_events or [],
            alert_ids=inv.related_alerts or [],
            investigation_id=investigation_id
        )

        # Build Subgraph
        primary_entity = inv.root_entities[0] if inv.root_entities else "user:victim"
        subgraph = in_memory_graph.get_neighborhood(primary_entity, depth=2, max_nodes=50)

        # Attack Paths
        attack_paths = []
        if len(inv.root_entities) >= 2:
            p = graph_algorithms.detect_attack_path(inv.root_entities[0], inv.root_entities[1])
            if p:
                attack_paths.append(p)

        # Generate Deterministic Security Story
        security_story = InvestigationService.generate_security_story(ev_list, alt_list)

        return InvestigationWorkbenchResponse(
            id=inv.id,
            title=inv.title,
            status=inv.status,
            priority=inv.priority,
            summary=inv.summary,
            confidence=inv.confidence or 0.75,
            risk_score=inv.risk_score or 50,
            assigned_to=inv.assigned_to,
            root_entities=inv.root_entities or [],
            related_events=inv.related_events or [],
            related_alerts=inv.related_alerts or [],
            mitre_tactics=inv.mitre_tactics or [],
            created_at=inv.created_at,
            updated_at=inv.updated_at,
            subgraph=subgraph,
            attack_paths=attack_paths,
            timeline=timeline,
            notes=notes,
            evidence=evidence,
            security_story=security_story
        )

    @staticmethod
    async def attach_evidence(
        session: AsyncSession,
        investigation_id: str,
        evidence_in: EvidenceCreate,
        collector: str
    ) -> Evidence:
        content_bytes = (evidence_in.content_text or "").encode("utf-8")
        computed_hash = evidence_in.sha256 or hashlib.sha256(content_bytes).hexdigest()

        evidence = Evidence(
            investigation_id=investigation_id,
            evidence_type=evidence_in.evidence_type,
            source=evidence_in.source,
            description=evidence_in.description,
            content_text=evidence_in.content_text,
            file_path=evidence_in.file_path,
            sha256=computed_hash,
            size_bytes=len(content_bytes),
            collector_user=collector
        )
        session.add(evidence)
        await session.commit()
        await session.refresh(evidence)
        return evidence


investigation_service = InvestigationService()
