from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime, timezone


class EventCreate(BaseModel):
    event_id: Optional[str] = Field(None, description="Optional caller-supplied event identifier")
    timestamp: Optional[datetime] = Field(None, description="ISO timestamp of event occurrence")
    source: str = Field(default="synthetic-stream", description="Log source system (e.g., linux-auth, sysmon, aws-cloudtrail)")
    event_type: str = Field(..., description="High-level category (authentication, process, network, file, privilege)")
    action: str = Field(..., description="Observed event action (login_failed, process_created, file_modified, outbound_conn)")
    user: Optional[str] = Field(None, description="User identity or account name")
    host: Optional[str] = Field(None, description="Hostname or endpoint identifier")
    source_ip: Optional[str] = Field(None, description="Originating IPv4/IPv6 address")
    destination_ip: Optional[str] = Field(None, description="Destination IPv4/IPv6 address")
    domain: Optional[str] = Field(None, description="DNS domain name")
    url: Optional[str] = Field(None, description="HTTP/HTTPS URL")
    process: Optional[str] = Field(None, description="Executable process name")
    parent_process: Optional[str] = Field(None, description="Parent executable name")
    file_path: Optional[str] = Field(None, description="Accessed file path")
    hash: Optional[str] = Field(None, description="SHA-256 or MD5 hash")
    resource: Optional[str] = Field(None, description="Target cloud resource or database ARN")
    severity: str = Field(default="informational", description="informational, low, medium, high, critical")
    raw_event: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Original raw event payload")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context tags")


class NormalizedEventResponse(BaseModel):
    id: str
    timestamp: datetime
    source: str
    event_type: str
    action: str
    user_identity: Optional[str] = None
    host: Optional[str] = None
    source_ip: Optional[str] = None
    destination_ip: Optional[str] = None
    domain: Optional[str] = None
    url: Optional[str] = None
    process_name: Optional[str] = None
    parent_process: Optional[str] = None
    file_path: Optional[str] = None
    file_hash: Optional[str] = None
    resource_id: Optional[str] = None
    severity: str
    raw_event: Dict[str, Any]
    metadata_json: Dict[str, Any]
    created_at: datetime


class BulkEventCreate(BaseModel):
    events: List[EventCreate]


class BulkIngestionResponse(BaseModel):
    received_count: int
    ingested_count: int
    extracted_entities_count: int
    graph_edges_created: int
    alerts_triggered_count: int
    event_ids: List[str]
