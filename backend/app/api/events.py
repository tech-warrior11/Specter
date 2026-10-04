from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional
from datetime import datetime

from app.database.database import get_db
from app.models.event import Event
from app.schemas.event import (
    EventCreate,
    NormalizedEventResponse,
    BulkEventCreate,
    BulkIngestionResponse
)
from app.services.ingestion import ingestion_service

router = APIRouter(prefix="/events", tags=["Events"])


@router.get("", response_model=List[NormalizedEventResponse])
async def list_events(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    event_type: Optional[str] = None,
    severity: Optional[str] = None,
    user: Optional[str] = None,
    host: Optional[str] = None,
    source_ip: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Retrieves paginated normalized security events with analytical filtering."""
    query = select(Event).order_by(desc(Event.timestamp))

    if event_type:
        query = query.where(Event.event_type == event_type.lower())
    if severity:
        query = query.where(Event.severity == severity.lower())
    if user:
        query = query.where(Event.user_identity == user.lower())
    if host:
        query = query.where(Event.host == host.upper())
    if source_ip:
        query = query.where(Event.source_ip == source_ip)

    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    events = result.scalars().all()
    return events


@router.get("/{event_id}", response_model=NormalizedEventResponse)
async def get_event_by_id(event_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieves a single security event including raw telemetry payload."""
    stmt = select(Event).where(Event.id == event_id)
    result = await db.execute(stmt)
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Event {event_id} not found")
    return event


@router.post("", response_model=NormalizedEventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(event_in: EventCreate, db: AsyncSession = Depends(get_db)):
    """Ingests, normalizes, extracts entities, and creates graph connections for a single event."""
    normalized_event, _, _ = await ingestion_service.ingest_event(db, event_in)
    return normalized_event


@router.post("/bulk", response_model=BulkIngestionResponse, status_code=status.HTTP_201_CREATED)
async def create_bulk_events(payload: BulkEventCreate, db: AsyncSession = Depends(get_db)):
    """Batch ingestion of multiple security events."""
    return await ingestion_service.ingest_bulk_events(db, payload.events)
