from typing import Dict, Any, List
from pydantic import BaseModel


class MITRETechnique(BaseModel):
    id: str  # T1110
    name: str  # Brute Force
    tactic: str  # Credential Access
    description: str
    detection_count: int
    alerts_triggered_count: int


class MITRETacticCoverage(BaseModel):
    tactic: str
    techniques_covered_count: int
    total_detections: int
    techniques: List[MITRETechnique]


class MITREMatrixResponse(BaseModel):
    tactics: List[MITRETacticCoverage]
    total_coverage_techniques: int
    total_active_detections: int
