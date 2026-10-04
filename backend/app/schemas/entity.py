from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from datetime import datetime


class ExtractedEntity(BaseModel):
    id: str  # e.g., "ip:10.10.10.50", "user:alice", "host:LAB-PC-01"
    entity_type: str  # USER, HOST, IP, DOMAIN, URL, PROCESS, FILE, HASH, RESOURCE
    value: str
    role: str = "subject"  # source, target, actor, object
    metadata: Dict[str, Any] = {}


class EntityResponse(BaseModel):
    id: str
    entity_type: str
    value: str
    risk_score: float
    criticality: str
    first_seen: datetime
    last_seen: datetime
    metadata_json: Dict[str, Any]
    created_at: datetime


class EntityProfileResponse(BaseModel):
    entity: EntityResponse
    related_entities_count: int
    related_events_count: int
    related_alerts_count: int
    recent_events: List[Dict[str, Any]]
    recent_alerts: List[Dict[str, Any]]
    blast_radius: Dict[str, Any]
