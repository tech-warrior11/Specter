from sqlalchemy import Column, String, Float, Integer, Text, DateTime, JSON, ForeignKey
from datetime import datetime, timezone
import uuid
from app.database.database import Base


class Investigation(Base):
    __tablename__ = "investigations"

    id = Column(String(64), primary_key=True, default=lambda: f"inv-{uuid.uuid4().hex[:12]}")
    title = Column(String(255), nullable=False)
    status = Column(String(32), default="OPEN", index=True)      # OPEN, IN_PROGRESS, ESCALATED, CLOSED
    priority = Column(String(32), default="HIGH", index=True)    # LOW, MEDIUM, HIGH, CRITICAL
    summary = Column(Text, nullable=True)
    confidence = Column(Float, default=0.75)
    risk_score = Column(Integer, default=50, index=True)
    assigned_to = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    root_entities = Column(JSON, default=list)
    related_events = Column(JSON, default=list)
    related_alerts = Column(JSON, default=list)
    mitre_tactics = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class InvestigationNote(Base):
    __tablename__ = "investigation_notes"

    id = Column(String(64), primary_key=True, default=lambda: f"note-{uuid.uuid4().hex[:12]}")
    investigation_id = Column(String(64), ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False, index=True)
    author_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    content = Column(Text, nullable=False)
    related_entity_id = Column(String(64), nullable=True)
    related_event_id = Column(String(64), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
