from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional

from app.database.database import get_db
from app.models.entity import Entity
from app.models.event import Event
from app.schemas.entity import EntityResponse, EntityProfileResponse
from app.schemas.graph import SubGraph
from app.graph.in_memory_graph import in_memory_graph
from app.graph.graph_algorithms import graph_algorithms

router = APIRouter(prefix="/entities", tags=["Entities"])


@router.get("", response_model=List[EntityResponse])
async def list_entities(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    entity_type: Optional[str] = None,
    min_risk: Optional[float] = None,
    db: AsyncSession = Depends(get_db)
):
    """Lists discovered security entities across all endpoints and accounts."""
    query = select(Entity).order_by(desc(Entity.risk_score), desc(Entity.last_seen))

    if entity_type:
        query = query.where(Entity.entity_type == entity_type.upper())
    if min_risk is not None:
        query = query.where(Entity.risk_score >= min_risk)

    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{entity_id:path}/profile", response_model=EntityProfileResponse)
async def get_entity_profile(entity_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieves deep entity profile including blast radius, recent events, and risk factors."""
    stmt = select(Entity).where(Entity.id == entity_id)
    result = await db.execute(stmt)
    entity = result.scalar_one_or_none()
    if not entity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Entity {entity_id} not found")

    # Fetch recent related events
    events_stmt = (
        select(Event)
        .where(
            (Event.user_identity == entity.value) |
            (Event.host == entity.value) |
            (Event.source_ip == entity.value) |
            (Event.destination_ip == entity.value) |
            (Event.process_name == entity.value) |
            (Event.file_path == entity.value)
        )
        .order_by(desc(Event.timestamp))
        .limit(10)
    )
    events_res = await db.execute(events_stmt)
    events = events_res.scalars().all()

    # Calculate blast radius via graph algorithms
    blast = graph_algorithms.calculate_blast_radius(entity_id, depth=2)
    neighborhood = in_memory_graph.get_neighborhood(entity_id, depth=1)

    return EntityProfileResponse(
        entity=EntityResponse(
            id=entity.id,
            entity_type=entity.entity_type,
            value=entity.value,
            risk_score=entity.risk_score,
            criticality=entity.criticality,
            first_seen=entity.first_seen,
            last_seen=entity.last_seen,
            metadata_json=entity.metadata_json or {},
            created_at=entity.created_at
        ),
        related_entities_count=len(neighborhood.nodes) - 1 if len(neighborhood.nodes) > 0 else 0,
        related_events_count=len(events),
        related_alerts_count=0,
        recent_events=[{"id": e.id, "timestamp": e.timestamp.isoformat(), "action": e.action, "severity": e.severity} for e in events],
        recent_alerts=[],
        blast_radius=blast
    )


@router.get("/{entity_id:path}/related", response_model=SubGraph)
async def get_related_entities(
    entity_id: str,
    depth: int = Query(1, ge=1, le=3),
    max_nodes: int = Query(50, ge=5, le=200)
):
    """Returns the k-hop subgraph centered around the target entity."""
    return in_memory_graph.get_neighborhood(entity_id, depth=depth, max_nodes=max_nodes)
