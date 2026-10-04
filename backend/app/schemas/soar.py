from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class SOARActionRequest(BaseModel):
    action_type: str = Field(..., description="Action type: BLOCK_IP, ISOLATE_HOST, DISABLE_USER, KILL_PROCESS, TRIGGER_WEBHOOK")
    target: str = Field(..., description="Target identifier (e.g. 198.51.100.25, LAB-PC-01, alice, powershell.exe)")
    reason: Optional[str] = Field(None, description="SOC Analyst justification for containment")
    alert_id: Optional[str] = None
    investigation_id: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)


class SOARActionResponse(BaseModel):
    id: str
    action_type: str
    target: str
    status: str
    initiated_by: str
    reason: Optional[str]
    execution_output: Dict[str, Any]
    rollback_supported: bool
    is_rolled_back: bool
    alert_id: Optional[str]
    investigation_id: Optional[str]
    created_at: datetime


class SOARPlaybookCreate(BaseModel):
    name: str
    description: Optional[str] = None
    trigger_rule_category: str
    severity_threshold: str = "HIGH"
    enabled: bool = True
    actions_sequence: List[Dict[str, Any]]


class SOARPlaybookResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    trigger_rule_category: str
    severity_threshold: str
    enabled: bool
    actions_sequence: List[Dict[str, Any]]
    execution_count: int
    created_at: datetime


class WebhookCreate(BaseModel):
    name: str
    webhook_type: str = Field(..., description="SLACK, DISCORD, PAGERDUTY, TEAMS, GENERIC")
    url: str
    enabled: bool = True
    events: List[str] = ["CRITICAL_ALERT", "INCIDENT_CREATED", "CONTAINMENT_TRIGGERED"]
    secret_token: Optional[str] = None


class WebhookResponse(BaseModel):
    id: str
    name: str
    webhook_type: str
    url: str
    enabled: bool
    events: List[str]
    last_triggered: Optional[datetime]
    created_at: datetime


class WebhookTestRequest(BaseModel):
    url: str
    webhook_type: str = "SLACK"
    message: Optional[str] = "🛡️ Specter Live SOAR Webhook Test Alert: Critical Attack Chain Blocked!"
