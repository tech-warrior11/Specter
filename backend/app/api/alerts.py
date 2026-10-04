from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional
from datetime import datetime, timezone

from app.database.database import get_db
from app.models.alert import Alert
from app.models.audit_log import AuditLog
from app.schemas.alert import AlertResponse, AlertStatusUpdate

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("", response_model=List[AlertResponse])
async def list_alerts(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    severity: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    rule_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Retrieves triggered security detection alerts with triage filters."""
    query = select(Alert).order_by(desc(Alert.created_at))

    if severity:
        query = query.where(Alert.severity == severity.lower())
    if status_filter:
        query = query.where(Alert.status == status_filter.upper())
    if rule_id:
        query = query.where(Alert.rule_id == rule_id)

    query = query.limit(limit).offset(offset)
    res = await db.execute(query)
    return res.scalars().all()


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(alert_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieves single alert and supporting event references."""
    alert = await db.get(Alert, alert_id)
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Alert {alert_id} not found")
    return alert


@router.patch("/{alert_id}", response_model=AlertResponse)
async def update_alert_status(
    alert_id: str,
    payload: AlertStatusUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Updates alert triage status or flags False Positive with auditable reason."""
    alert = await db.get(Alert, alert_id)
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Alert {alert_id} not found")

    old_status = alert.status
    alert.status = payload.status.upper()
    if payload.fp_reason:
        alert.fp_reason = payload.fp_reason
    if payload.fp_marked_by:
        alert.fp_marked_by = payload.fp_marked_by

    # Create immutable audit log
    audit = AuditLog(
        actor=payload.fp_marked_by or "analyst",
        action="ALERT_STATUS_UPDATE",
        resource=f"alert:{alert_id}",
        metadata_json={
            "old_status": old_status,
            "new_status": alert.status,
            "fp_reason": payload.fp_reason
        }
    )
    db.add(audit)
    await db.commit()
    await db.refresh(alert)
    return alert
