from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import Dict, Any, List

from app.database.database import get_db
from app.models.event import Event
from app.models.alert import Alert
from app.models.investigation import Investigation
from app.models.incident import Incident
from app.models.entity import Entity
from app.models.behavior import Anomaly
from app.models.ioc import IOC
from app.graph.in_memory_graph import in_memory_graph

router = APIRouter(prefix="/dashboard", tags=["SOC Dashboard"])


@router.get("/summary")
async def get_dashboard_summary(db: AsyncSession = Depends(get_db)):
    """Provides high-level SOC executive dashboard KPIs, risk levels, and top entities."""
    # Counts
    ev_count = await db.scalar(select(func.count(Event.id))) or 0
    alt_count = await db.scalar(select(func.count(Alert.id))) or 0
    inv_open_count = await db.scalar(select(func.count(Investigation.id)).where(Investigation.status == "OPEN")) or 0
    inc_open_count = await db.scalar(select(func.count(Incident.id)).where(Incident.status == "OPEN")) or 0
    ano_count = await db.scalar(select(func.count(Anomaly.id))) or 0
    ioc_count = await db.scalar(select(func.count(IOC.id))) or 0

    # Severity distribution
    sev_query = select(Alert.severity, func.count(Alert.id)).group_by(Alert.severity)
    sev_res = await db.execute(sev_query)
    severity_dist = {row[0]: row[1] for row in sev_res.all()}

    # MITRE tactics distribution
    mitre_query = select(Alert.mitre_tactic, func.count(Alert.id)).where(Alert.mitre_tactic != None).group_by(Alert.mitre_tactic)
    mitre_res = await db.execute(mitre_query)
    mitre_dist = [{"tactic": row[0], "count": row[1]} for row in mitre_res.all()]

    # High-Risk Entities
    ents_query = select(Entity).order_by(desc(Entity.risk_score), desc(Entity.last_seen)).limit(6)
    ents_res = await db.execute(ents_query)
    top_entities = [
        {
            "id": e.id,
            "type": e.entity_type,
            "value": e.value,
            "risk_score": e.risk_score,
            "criticality": e.criticality
        }
        for e in ents_res.scalars().all()
    ]

    graph_stats = in_memory_graph.get_stats()

    return {
        "kpis": {
            "total_events": ev_count,
            "total_alerts": alt_count,
            "open_investigations": inv_open_count,
            "open_incidents": inc_open_count,
            "anomalies_detected": ano_count,
            "active_iocs": ioc_count,
            "graph_nodes": graph_stats["node_count"],
            "graph_edges": graph_stats["edge_count"]
        },
        "alerts_by_severity": {
            "critical": severity_dist.get("critical", 0),
            "high": severity_dist.get("high", 0),
            "medium": severity_dist.get("medium", 0),
            "low": severity_dist.get("low", 0),
            "informational": severity_dist.get("informational", 0)
        },
        "mitre_distribution": mitre_dist,
        "high_risk_entities": top_entities
    }


@router.get("/timeline")
async def get_dashboard_timeline(db: AsyncSession = Depends(get_db)):
    """Returns aggregated event velocity and alert trends."""
    recent_events = await db.execute(select(Event).order_by(desc(Event.timestamp)).limit(50))
    events = recent_events.scalars().all()

    # Bucketing by 5-minute segments
    buckets: Dict[str, Dict[str, int]] = {}
    for ev in events:
        time_key = ev.timestamp.strftime("%H:%M")
        if time_key not in buckets:
            buckets[time_key] = {"events": 0, "alerts": 0}
        buckets[time_key]["events"] += 1

    chart_data = [{"time": k, "events": v["events"], "alerts": v["alerts"]} for k, v in sorted(buckets.items())]
    return {"timeline_series": chart_data}
