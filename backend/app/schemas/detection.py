from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from datetime import datetime


class DetectionRuleCreate(BaseModel):
    id: str
    name: str
    severity: str
    event_type: str
    condition: Dict[str, Any]
    threshold: Dict[str, Any]
    group_by: List[str]
    mitre_tactic: Optional[str] = None
    mitre_technique_id: Optional[str] = None
    mitre_technique_name: Optional[str] = None
    description: str
    enabled: bool = True


class DetectionRuleUpdate(BaseModel):
    enabled: Optional[bool] = None
    severity: Optional[str] = None
    threshold: Optional[Dict[str, Any]] = None
    description: Optional[str] = None


class DetectionRuleResponse(BaseModel):
    id: str
    name: str
    severity: str
    event_type: str
    condition: Dict[str, Any]
    threshold: Dict[str, Any]
    group_by: List[str]
    mitre_tactic: Optional[str] = None
    mitre_technique_id: Optional[str] = None
    mitre_technique_name: Optional[str] = None
    description: str
    enabled: bool
    trigger_count: int
    false_positive_count: int
    created_at: datetime
    updated_at: datetime
