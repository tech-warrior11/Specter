from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, JSON, Text
from datetime import datetime, timezone
import uuid
from app.database.database import Base


class SOARAction(Base):
    __tablename__ = "soar_actions"

    id = Column(String(64), primary_key=True, default=lambda: f"act-{uuid.uuid4().hex[:10]}")
    action_type = Column(String(64), nullable=False, index=True)  # BLOCK_IP, ISOLATE_HOST, DISABLE_USER, KILL_PROCESS, TRIGGER_WEBHOOK
    target = Column(String(255), nullable=False, index=True)      # e.g., 198.51.100.25, LAB-PC-01, alice, powershell.exe
    status = Column(String(32), nullable=False, default="SUCCESS", index=True)  # SUCCESS, PENDING, FAILED, ROLLED_BACK
    initiated_by = Column(String(64), nullable=False, default="admin")
    reason = Column(Text, nullable=True)
    execution_output = Column(JSON, default=dict)
    rollback_supported = Column(Boolean, default=True)
    is_rolled_back = Column(Boolean, default=False)
    alert_id = Column(String(64), nullable=True)
    investigation_id = Column(String(64), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class SOARPlaybook(Base):
    __tablename__ = "soar_playbooks"

    id = Column(String(64), primary_key=True, default=lambda: f"pbk-{uuid.uuid4().hex[:8]}")
    name = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)
    trigger_rule_category = Column(String(64), nullable=False)  # Authentication, Execution, Exfiltration, Multi-Stage, All
    severity_threshold = Column(String(32), default="HIGH")     # MEDIUM, HIGH, CRITICAL
    enabled = Column(Boolean, default=True)
    actions_sequence = Column(JSON, default=list)  # e.g. [{"action": "BLOCK_IP"}, {"action": "ISOLATE_HOST"}, {"action": "TRIGGER_WEBHOOK"}]
    execution_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class WebhookConfig(Base):
    __tablename__ = "webhook_configs"

    id = Column(String(64), primary_key=True, default=lambda: f"whk-{uuid.uuid4().hex[:8]}")
    name = Column(String(128), nullable=False)
    webhook_type = Column(String(32), nullable=False)  # SLACK, DISCORD, PAGERDUTY, TEAMS, GENERIC
    url = Column(String(512), nullable=False)
    enabled = Column(Boolean, default=True)
    events = Column(JSON, default=lambda: ["CRITICAL_ALERT", "INCIDENT_CREATED", "CONTAINMENT_TRIGGERED"])
    secret_token = Column(String(128), nullable=True)
    last_triggered = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
