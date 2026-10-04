from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from datetime import datetime


class ReportGenerateRequest(BaseModel):
    report_type: str  # investigation, incident, threat_hunt, executive_summary
    target_id: Optional[str] = None
    title: Optional[str] = None
    include_timeline: bool = True
    include_graph_topology: bool = True
    include_mitre: bool = True
    include_evidence: bool = True


class ReportResponse(BaseModel):
    report_id: str
    report_type: str
    title: str
    generated_at: datetime
    content_markdown: str
    risk_score: int
    key_findings: List[str]
    mitre_summary: List[str]
    evidence_items_count: int
