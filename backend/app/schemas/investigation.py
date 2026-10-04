from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from datetime import datetime
from app.schemas.graph import SubGraph, AttackPath


class InvestigationCreate(BaseModel):
    title: str
    priority: str = "HIGH"  # LOW, MEDIUM, HIGH, CRITICAL
    summary: Optional[str] = None
    root_entities: List[str] = []
    related_events: List[str] = []
    related_alerts: List[str] = []
    assigned_to: Optional[str] = None


class InvestigationNoteCreate(BaseModel):
    content: str
    related_entity_id: Optional[str] = None
    related_event_id: Optional[str] = None


class InvestigationNoteResponse(BaseModel):
    id: str
    investigation_id: str
    author_id: Optional[str]
    content: str
    related_entity_id: Optional[str]
    related_event_id: Optional[str]
    created_at: datetime


class EvidenceCreate(BaseModel):
    evidence_type: str  # log_snippet, network_capture, memory_dump, text_note, file_hash
    source: str
    description: str
    content_text: Optional[str] = None
    file_path: Optional[str] = None
    sha256: Optional[str] = None  # If not provided, computed automatically


class EvidenceResponse(BaseModel):
    id: str
    investigation_id: str
    evidence_type: str
    source: str
    description: str
    content_text: Optional[str]
    sha256: str
    size_bytes: int
    collector_user: str
    collected_at: datetime


class TimelineEntry(BaseModel):
    timestamp: datetime
    entry_type: str  # event, alert, note, action
    title: str
    description: str
    entity: Optional[str] = None
    severity: str = "informational"
    reference_id: str


class InvestigationWorkbenchResponse(BaseModel):
    id: str
    title: str
    status: str
    priority: str
    summary: Optional[str]
    confidence: float
    risk_score: int
    assigned_to: Optional[str]
    root_entities: List[str]
    related_events: List[str]
    related_alerts: List[str]
    mitre_tactics: List[str]
    created_at: datetime
    updated_at: datetime
    subgraph: SubGraph
    attack_paths: List[AttackPath]
    timeline: List[TimelineEntry]
    notes: List[InvestigationNoteResponse]
    evidence: List[EvidenceResponse]
    security_story: str
