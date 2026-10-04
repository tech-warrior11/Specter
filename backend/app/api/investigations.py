from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional, Dict, Any

from app.database.database import get_db
from app.models.investigation import Investigation, InvestigationNote
from app.models.evidence import Evidence
from app.models.audit_log import AuditLog
from app.schemas.investigation import (
    InvestigationWorkbenchResponse,
    InvestigationCreate,
    InvestigationNoteCreate,
    InvestigationNoteResponse,
    EvidenceCreate,
    EvidenceResponse
)
from app.services.investigation import investigation_service

router = APIRouter(prefix="/investigations", tags=["Investigations"])


@router.get("", response_model=List[Dict[str, Any]] if False else Any)
async def list_investigations(
    status_filter: Optional[str] = Query(None, alias="status"),
    priority: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Lists open and archived investigation cases."""
    query = select(Investigation).order_by(desc(Investigation.created_at))
    if status_filter:
        query = query.where(Investigation.status == status_filter.upper())
    if priority:
        query = query.where(Investigation.priority == priority.upper())

    res = await db.execute(query)
    invs = res.scalars().all()
    return [
        {
            "id": i.id,
            "title": i.title,
            "status": i.status,
            "priority": i.priority,
            "summary": i.summary,
            "risk_score": i.risk_score,
            "root_entities": i.root_entities or [],
            "alerts_count": len(i.related_alerts or []),
            "events_count": len(i.related_events or []),
            "created_at": i.created_at,
            "updated_at": i.updated_at
        }
        for i in invs
    ]


@router.post("", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_investigation(payload: InvestigationCreate, db: AsyncSession = Depends(get_db)):
    """Creates a new stateful investigation workbench."""
    inv = Investigation(
        title=payload.title,
        status="OPEN",
        priority=payload.priority.upper(),
        summary=payload.summary or f"Manual investigation created for {len(payload.root_entities)} root entities.",
        root_entities=payload.root_entities,
        related_events=payload.related_events,
        related_alerts=payload.related_alerts,
        assigned_to=payload.assigned_to
    )
    db.add(inv)
    await db.commit()
    await db.refresh(inv)

    audit = AuditLog(actor="analyst", action="CASE_CREATE", resource=f"investigation:{inv.id}")
    db.add(audit)
    await db.commit()

    return {"id": inv.id, "title": inv.title, "status": inv.status}


@router.get("/{investigation_id}", response_model=InvestigationWorkbenchResponse)
async def get_investigation_workbench(investigation_id: str, db: AsyncSession = Depends(get_db)):
    """Returns complete investigation workbench with attack graph, timeline, and security story."""
    try:
        return await investigation_service.get_workbench(db, investigation_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{investigation_id}/notes", response_model=InvestigationNoteResponse, status_code=status.HTTP_201_CREATED)
async def add_investigation_note(
    investigation_id: str,
    payload: InvestigationNoteCreate,
    db: AsyncSession = Depends(get_db)
):
    """Adds an analyst observation or hypothesis to the case."""
    inv = await db.get(Investigation, investigation_id)
    if not inv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investigation not found")

    note = InvestigationNote(
        investigation_id=investigation_id,
        content=payload.content,
        related_entity_id=payload.related_entity_id,
        related_event_id=payload.related_event_id
    )
    db.add(note)
    await db.commit()
    await db.refresh(note)
    return note


@router.post("/{investigation_id}/evidence", response_model=EvidenceResponse, status_code=status.HTTP_201_CREATED)
async def attach_case_evidence(
    investigation_id: str,
    payload: EvidenceCreate,
    db: AsyncSession = Depends(get_db)
):
    """Attaches forensic evidence with automatic cryptographic SHA-256 verification."""
    inv = await db.get(Investigation, investigation_id)
    if not inv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investigation not found")

    evidence = await investigation_service.attach_evidence(
        session=db,
        investigation_id=investigation_id,
        evidence_in=payload,
        collector="analyst"
    )
    return evidence
