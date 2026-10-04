from sqlalchemy import Column, String, DateTime, JSON
from datetime import datetime, timezone
import uuid
from app.database.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(64), primary_key=True, default=lambda: f"aud-{uuid.uuid4().hex[:12]}")
    actor = Column(String(64), nullable=False, index=True)      # username or system service
    action = Column(String(64), nullable=False, index=True)     # LOGIN, RULE_UPDATE, FP_FLAG, CASE_CREATE
    resource = Column(String(128), nullable=False, index=True)  # alert:alt-123, rule:DET-AUTH-001
    ip_address = Column(String(64), nullable=True)
    metadata_json = Column(JSON, default=dict)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
