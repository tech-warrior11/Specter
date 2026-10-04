from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from datetime import datetime


class HuntQueryRequest(BaseModel):
    query: str  # e.g., 'source_ip = "10.10.10.50" AND severity >= "medium"'
    time_window_hours: Optional[int] = 24
    limit: int = 100


class SavedHuntCreate(BaseModel):
    name: str
    description: Optional[str] = None
    query_dsl: Dict[str, Any]
    raw_query: str


class SavedHuntResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    query_dsl: Dict[str, Any]
    raw_query: str
    created_by: Optional[str]
    created_at: datetime


class HuntResultResponse(BaseModel):
    query: str
    total_matches: int
    events: List[Dict[str, Any]]
    entities: List[Dict[str, Any]]
    suggested_pivots: List[str]
