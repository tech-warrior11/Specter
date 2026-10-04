from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class GraphNode(BaseModel):
    id: str = Field(..., description="Unique deterministic node ID, e.g., 'user:alice'")
    label: str = Field(..., description="Node label/category, e.g., 'User', 'Host', 'IP'")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary node metadata")


class GraphEdge(BaseModel):
    id: str = Field(..., description="Unique edge ID, e.g., 'rel:user:alice-ip:10.10.10.50'")
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    relation_type: str = Field(..., description="Relationship type, e.g., 'LOGGED_FROM_IP'")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Edge metadata such as timestamp, weight")


class SubGraph(BaseModel):
    nodes: List[GraphNode] = Field(default_factory=list)
    edges: List[GraphEdge] = Field(default_factory=list)


class AttackPath(BaseModel):
    path_id: str
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    confidence: float
    risk_score: int
    stage_progression: List[str] = Field(default_factory=list)
    evidence_event_ids: List[str] = Field(default_factory=list)
    description: str
