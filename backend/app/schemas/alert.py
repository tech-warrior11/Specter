from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from datetime import datetime


class AlertCreate(BaseModel):
    rule_id: Optional[str] = None
    title: str
    description: str
    severity: str
    confidence: float = 0.8
    risk_score: int = 50
    event_ids: List[str]
    entity_ids: List[str]
    mitre_tactic: Optional[str] = None
    mitre_technique: Optional[str] = None
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None


class AlertStatusUpdate(BaseModel):
    status: str  # NEW, ACKNOWLEDGED, INVESTIGATING, RESOLVED, FALSE_POSITIVE
    fp_reason: Optional[str] = None
    fp_marked_by: Optional[str] = None


class AlertResponse(BaseModel):
    id: str
    rule_id: Optional[str] = None
    title: str
    description: str
    severity: str
    confidence: float
    risk_score: int
    status: str
    event_ids: List[str]
    entity_ids: List[str]
    mitre_tactic: Optional[str] = None
    mitre_technique: Optional[str] = None
    first_seen: datetime
    last_seen: datetime
    fp_reason: Optional[str] = None
    fp_marked_by: Optional[str] = None
    created_at: datetime
