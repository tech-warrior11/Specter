from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Dict, Any
from datetime import datetime, timezone, timedelta
import re

from app.database.database import get_db
from app.models.event import Event
from app.models.entity import Entity
from app.models.hunt import HuntQuery
from app.schemas.hunt import HuntQueryRequest, HuntResultResponse, SavedHuntCreate, SavedHuntResponse

router = APIRouter(prefix="/hunting", tags=["Threat Hunting"])


def parse_dsl_conditions(query_str: str) -> List[Dict[str, str]]:
    """Simple parser for Threat Hunting DSL (e.g., 'user = "alice" AND severity >= "medium"')."""
    tokens = query_str.split(" AND ")
    conditions = []
    pattern = re.compile(r'(\w+)\s*(=|!=|>=|<=|CONTAINS)\s*["\']?([^"\']+)["\']?')

    for token in tokens:
        match = pattern.search(token.strip())
        if match:
            field, op, val = match.groups()
            conditions.append({"field": field.strip().lower(), "op": op, "value": val.strip()})
    return conditions


@router.post("/search", response_model=HuntResultResponse)
async def execute_hunt_search(payload: HuntQueryRequest, db: AsyncSession = Depends(get_db)):
    """Executes a proactive threat hunting query across the security telemetry store."""
    conditions = parse_dsl_conditions(payload.query)

    query = select(Event).order_by(desc(Event.timestamp))
    if payload.time_window_hours:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=payload.time_window_hours)
        query = query.where(Event.timestamp >= cutoff)

    for c in conditions:
        field, op, val = c["field"], c["op"], c["value"]
        if field == "user" or field == "user_identity":
            query = query.where(Event.user_identity == val.lower())
        elif field == "host":
            query = query.where(Event.host == val.upper())
        elif field == "source_ip":
            query = query.where(Event.source_ip == val)
        elif field == "destination_ip":
            query = query.where(Event.destination_ip == val)
        elif field == "event_type":
            query = query.where(Event.event_type == val.lower())
        elif field == "action":
            query = query.where(Event.action == val.lower())
        elif field == "process" or field == "process_name":
            query = query.where(Event.process_name == val.lower())
        elif field == "severity":
            query = query.where(Event.severity == val.lower())

    query = query.limit(payload.limit)
    res = await db.execute(query)
    events = res.scalars().all()

    # Extract matching entities
    user_pivots = list(set([e.user_identity for e in events if e.user_identity]))
    host_pivots = list(set([e.host for e in events if e.host]))
    ip_pivots = list(set([e.source_ip for e in events if e.source_ip] + [e.destination_ip for e in events if e.destination_ip]))

    suggested_pivots = (
        [f"user:{u}" for u in user_pivots[:5]] +
        [f"host:{h}" for h in host_pivots[:5]] +
        [f"ip:{i}" for i in ip_pivots[:5]]
    )

    ev_dicts = [
        {
            "id": e.id,
            "timestamp": e.timestamp.isoformat(),
            "source": e.source,
            "event_type": e.event_type,
            "action": e.action,
            "user": e.user_identity,
            "host": e.host,
            "source_ip": e.source_ip,
            "destination_ip": e.destination_ip,
            "process": e.process_name,
            "severity": e.severity
        }
        for e in events
    ]

    return HuntResultResponse(
        query=payload.query,
        total_matches=len(events),
        events=ev_dicts,
        entities=[{"type": "user", "values": user_pivots}, {"type": "host", "values": host_pivots}, {"type": "ip", "values": ip_pivots}],
        suggested_pivots=suggested_pivots
    )


@router.get("/saved", response_model=List[SavedHuntResponse])
async def list_saved_hunts(db: AsyncSession = Depends(get_db)):
    """Lists bookmarked hunting queries."""
    res = await db.execute(select(HuntQuery).order_by(desc(HuntQuery.created_at)))
    return res.scalars().all()


@router.post("/saved", response_model=SavedHuntResponse, status_code=status.HTTP_201_CREATED)
async def save_hunt_query(payload: SavedHuntCreate, db: AsyncSession = Depends(get_db)):
    """Saves a recurring threat hunting search."""
    hunt = HuntQuery(
        name=payload.name,
        description=payload.description,
        query_dsl=payload.query_dsl,
        raw_query=payload.raw_query
    )
    db.add(hunt)
    await db.commit()
    await db.refresh(hunt)
    return hunt
