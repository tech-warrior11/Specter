from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.database.database import get_db
from app.models.detection_rule import DetectionRule
from app.models.audit_log import AuditLog
from app.schemas.detection import DetectionRuleResponse, DetectionRuleUpdate
from app.services.detection import detection_engine

router = APIRouter(prefix="/detections", tags=["Detections"])


@router.get("/rules", response_model=List[DetectionRuleResponse])
async def list_detection_rules(
    enabled_only: bool = False,
    severity: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Lists loaded detection rules and trigger statistics."""
    # Ensure disk rules are synced
    await detection_engine.sync_rules_to_db(db)

    query = select(DetectionRule)
    if enabled_only:
        query = query.where(DetectionRule.enabled == True)
    if severity:
        query = query.where(DetectionRule.severity == severity.lower())

    res = await db.execute(query)
    return res.scalars().all()


@router.get("/rules/{rule_id}", response_model=DetectionRuleResponse)
async def get_detection_rule(rule_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieves specific detection rule definition and MITRE ATT&CK mapping."""
    rule = await db.get(DetectionRule, rule_id)
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Rule {rule_id} not found")
    return rule


@router.patch("/rules/{rule_id}", response_model=DetectionRuleResponse)
async def update_detection_rule(
    rule_id: str,
    payload: DetectionRuleUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Allows tuning of rule thresholds, enablement, and severity with audit trail."""
    rule = await db.get(DetectionRule, rule_id)
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Rule {rule_id} not found")

    if payload.enabled is not None:
        rule.enabled = payload.enabled
    if payload.severity is not None:
        rule.severity = payload.severity.lower()
    if payload.threshold is not None:
        rule.threshold = payload.threshold
    if payload.description is not None:
        rule.description = payload.description

    audit = AuditLog(
        actor="detection_engineer",
        action="RULE_TUNING",
        resource=f"rule:{rule_id}",
        metadata_json=payload.model_dump(exclude_unset=True)
    )
    db.add(audit)
    await db.commit()
    await db.refresh(rule)
    return rule
