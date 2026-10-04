from sqlalchemy import Column, String, Boolean, Integer, Text, DateTime, JSON
from datetime import datetime, timezone
from app.database.database import Base


class DetectionRule(Base):
    __tablename__ = "detection_rules"

    id = Column(String(64), primary_key=True)  # e.g. DET-AUTH-001
    name = Column(String(255), nullable=False)
    severity = Column(String(32), nullable=False, default="medium")  # informational, low, medium, high, critical
    event_type = Column(String(64), nullable=False, index=True)
    condition = Column(JSON, nullable=False)
    threshold = Column(JSON, nullable=False)
    group_by = Column(JSON, nullable=False)
    mitre_tactic = Column(String(64), nullable=True)
    mitre_technique_id = Column(String(32), nullable=True, index=True)
    mitre_technique_name = Column(String(128), nullable=True)
    description = Column(Text, nullable=False)
    enabled = Column(Boolean, default=True)
    trigger_count = Column(Integer, default=0)
    false_positive_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
