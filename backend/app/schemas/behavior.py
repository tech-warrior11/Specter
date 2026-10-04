from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from datetime import datetime


class BehaviorProfileResponse(BaseModel):
    id: str
    entity_id: str
    profile_type: str
    normal_login_hours: List[int]
    normal_hosts: List[str]
    normal_ips: List[str]
    normal_processes: List[str]
    avg_daily_events: float
    std_daily_events: float
    last_calculated: datetime


class AnomalyResponse(BaseModel):
    id: str
    entity_id: str
    anomaly_type: str
    score: float
    explanation: str
    event_ids: List[str]
    detected_at: datetime
