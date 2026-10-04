from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
import logging

from app.models.alert import Alert
from app.models.event import Event
from app.models.investigation import Investigation
from app.graph.graph_algorithms import graph_algorithms

logger = logging.getLogger("specter.services.correlation")


class CorrelationEngine:
    """Correlates security events and alerts into cohesive attack chains and incident candidates."""

    @staticmethod
    async def correlate_entity_alerts(session: AsyncSession, entity_id: str, window_hours: int = 24) -> Optional[Investigation]:
        """Correlates all recent alerts involving a specific entity and proposes an investigation."""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=window_hours)
        stmt = select(Alert).where(Alert.created_at >= cutoff).order_by(Alert.created_at)
        result = await session.execute(stmt)
        all_alerts = result.scalars().all()

        matching_alerts = [a for a in all_alerts if entity_id in (a.entity_ids or [])]
        if len(matching_alerts) < 2:
            return None

        # Aggregate event IDs & entity IDs
        all_ev_ids = []
        all_ent_ids = [entity_id]
        mitre_tactics = []
        for a in matching_alerts:
            all_ev_ids.extend(a.event_ids or [])
            all_ent_ids.extend(a.entity_ids or [])
            if a.mitre_tactic and a.mitre_tactic not in mitre_tactics:
                mitre_tactics.append(a.mitre_tactic)

        all_ev_ids = list(set(all_ev_ids))
        all_ent_ids = list(set(all_ent_ids))

        # Check if an active investigation already encompasses this entity
        inv_stmt = select(Investigation).where(Investigation.status == "OPEN")
        inv_res = await session.execute(inv_stmt)
        open_invs = inv_res.scalars().all()

        for inv in open_invs:
            if entity_id in (inv.root_entities or []):
                # Update existing investigation
                inv.related_alerts = list(set((inv.related_alerts or []) + [a.id for a in matching_alerts]))
                inv.related_events = list(set((inv.related_events or []) + all_ev_ids))
                inv.mitre_tactics = list(set((inv.mitre_tactics or []) + mitre_tactics))
                await session.commit()
                return inv

        # Create new auto-correlated Investigation candidate
        title = f"Correlated Attack-Chain Activity involving {entity_id}"
        summary = (
            f"Observed {len(matching_alerts)} correlated detection alerts and {len(all_ev_ids)} related security events "
            f"spanning tactics: {', '.join(mitre_tactics)}."
        )

        new_inv = Investigation(
            title=title,
            status="OPEN",
            priority="HIGH" if len(matching_alerts) >= 3 else "MEDIUM",
            summary=summary,
            confidence=min(0.95, 0.6 + (len(matching_alerts) * 0.1)),
            risk_score=min(100, 40 + (len(matching_alerts) * 15)),
            root_entities=[entity_id],
            related_events=all_ev_ids,
            related_alerts=[a.id for a in matching_alerts],
            mitre_tactics=mitre_tactics
        )
        session.add(new_inv)
        await session.commit()
        await session.refresh(new_inv)
        return new_inv


correlation_engine = CorrelationEngine()
