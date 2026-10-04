from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from datetime import datetime


class IncidentCreate(BaseModel):
    investigation_id: Optional[str] = None
    title: str
    severity: str = "high"
    summary: Optional[str] = None
    root_cause: Optional[str] = None
    affected_entities: List[str] = []
    response_actions: List[str] = []


class IncidentStatusUpdate(BaseModel):
    status: str  # OPEN, INVESTIGATING, CONTAINED, RECOVERY, CLOSED
    resolution: Optional[str] = None
    response_action: Optional[str] = None


class IncidentResponse(BaseModel):
    id: str
    investigation_id: Optional[str]
    title: str
    severity: str
    risk_score: int
    status: str
    summary: Optional[str]
    root_cause: Optional[str]
    affected_entities: List[str]
    response_actions: List[str]
    resolution: Optional[str]
    assigned_to: Optional[str]
    created_at: datetime
    updated_at: datetime
