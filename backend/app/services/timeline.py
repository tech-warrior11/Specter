from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
import logging

from app.models.event import Event
from app.models.alert import Alert
from app.models.investigation import InvestigationNote
from app.schemas.investigation import TimelineEntry

logger = logging.getLogger("specter.services.timeline")


class TimelineEngine:
    """Constructs unified chronological investigation timelines from events, alerts, and analyst notes."""

    @staticmethod
    async def build_timeline(
        session: AsyncSession,
        event_ids: List[str],
        alert_ids: List[str],
        investigation_id: Optional[str] = None
    ) -> List[TimelineEntry]:
        entries: List[TimelineEntry] = []

        # 1. Fetch Events
        if event_ids:
            ev_stmt = select(Event).where(Event.id.in_(event_ids))
            ev_res = await session.execute(ev_stmt)
            for ev in ev_res.scalars().all():
                entity_label = ev.user_identity or ev.host or ev.source_ip or "System"
                entries.append(TimelineEntry(
                    timestamp=ev.timestamp,
                    entry_type="event",
                    title=f"Event: {ev.action.replace('_', ' ').title()}",
                    description=f"{entity_label} executed {ev.action} on {ev.host or 'network'} via {ev.source}",
                    entity=entity_label,
                    severity=ev.severity,
                    reference_id=ev.id
                ))

        # 2. Fetch Alerts
        if alert_ids:
            alt_stmt = select(Alert).where(Alert.id.in_(alert_ids))
            alt_res = await session.execute(alt_stmt)
            for alt in alt_res.scalars().all():
                entries.append(TimelineEntry(
                    timestamp=alt.first_seen,
                    entry_type="alert",
                    title=f"Detection Alert: {alt.title}",
                    description=alt.description,
                    entity=", ".join(alt.entity_ids or []) if alt.entity_ids else "Unknown",
                    severity=alt.severity,
                    reference_id=alt.id
                ))

        # 3. Fetch Investigation Notes
        if investigation_id:
            note_stmt = select(InvestigationNote).where(InvestigationNote.investigation_id == investigation_id)
            note_res = await session.execute(note_stmt)
            for note in note_res.scalars().all():
                entries.append(TimelineEntry(
                    timestamp=note.created_at,
                    entry_type="note",
                    title="Analyst Observation",
                    description=note.content,
                    entity=note.related_entity_id,
                    severity="informational",
                    reference_id=note.id
                ))

        # Sort chronologically
        entries.sort(key=lambda x: x.timestamp)
        return entries


timeline_engine = TimelineEngine()
