from sqlalchemy import Column, String, Float, Integer, Text, DateTime, JSON, ForeignKey
from datetime import datetime, timezone
import uuid
from app.database.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String(64), primary_key=True, default=lambda: f"alt-{uuid.uuid4().hex[:12]}")
    rule_id = Column(String(64), ForeignKey("detection_rules.id", ondelete="SET NULL"), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String(32), nullable=False, index=True)  # informational, low, medium, high, critical
    confidence = Column(Float, default=0.8)
    risk_score = Column(Integer, default=50, index=True)
    status = Column(String(32), default="NEW", index=True)    # NEW, ACKNOWLEDGED, INVESTIGATING, RESOLVED, FALSE_POSITIVE
    event_ids = Column(JSON, nullable=False, default=list)
    entity_ids = Column(JSON, nullable=False, default=list)
    mitre_tactic = Column(String(64), nullable=True)
    mitre_technique = Column(String(128), nullable=True)
    first_seen = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    last_seen = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    fp_reason = Column(Text, nullable=True)
    fp_marked_by = Column(String(64), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
