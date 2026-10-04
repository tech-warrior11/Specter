from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional

from app.database.database import get_db
from app.models.incident import Incident
from app.models.audit_log import AuditLog
from app.schemas.incident import IncidentResponse, IncidentCreate, IncidentStatusUpdate

router = APIRouter(prefix="/incidents", tags=["Incidents"])


@router.get("", response_model=List[IncidentResponse])
async def list_incidents(
    status_filter: Optional[str] = Query(None, alias="status"),
    severity: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Lists security incidents with operational lifecycle filters."""
    query = select(Incident).order_by(desc(Incident.created_at))
    if status_filter:
        query = query.where(Incident.status == status_filter.upper())
    if severity:
        query = query.where(Incident.severity == severity.lower())

    res = await db.execute(query)
    return res.scalars().all()


@router.post("", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
async def create_incident(payload: IncidentCreate, db: AsyncSession = Depends(get_db)):
    """Escalates an investigation or creates a formal security incident."""
    inc = Incident(
        investigation_id=payload.investigation_id,
        title=payload.title,
        severity=payload.severity.lower(),
        summary=payload.summary,
        root_cause=payload.root_cause,
        affected_entities=payload.affected_entities,
        response_actions=payload.response_actions,
        status="OPEN"
    )
    db.add(inc)
    await db.commit()
    await db.refresh(inc)

    audit = AuditLog(actor="soc_lead", action="INCIDENT_CREATE", resource=f"incident:{inc.id}")
    db.add(audit)
    await db.commit()

    return inc


@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(incident_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieves incident details, root cause, and containment timeline."""
    inc = await db.get(Incident, incident_id)
    if not inc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")
    return inc


@router.patch("/{incident_id}", response_model=IncidentResponse)
async def update_incident_status(
    incident_id: str,
    payload: IncidentStatusUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Updates incident status (OPEN -> INVESTIGATING -> CONTAINED -> RECOVERY -> CLOSED) and containment action."""
    inc = await db.get(Incident, incident_id)
    if not inc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")

    inc.status = payload.status.upper()
    if payload.resolution:
        inc.resolution = payload.resolution
    if payload.response_action:
        current_actions = list(inc.response_actions or [])
        current_actions.append(payload.response_action)
        inc.response_actions = current_actions

    audit = AuditLog(
        actor="soc_analyst",
        action="INCIDENT_UPDATE",
        resource=f"incident:{incident_id}",
        metadata_json={"new_status": inc.status, "action": payload.response_action}
    )
    db.add(audit)
    await db.commit()
    await db.refresh(inc)
    return inc
