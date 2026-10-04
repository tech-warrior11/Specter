from sqlalchemy import Column, String, Integer, Text, DateTime, JSON, ForeignKey
from datetime import datetime, timezone
import uuid
from app.database.database import Base


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(String(64), primary_key=True, default=lambda: f"inc-{uuid.uuid4().hex[:12]}")
    investigation_id = Column(String(64), ForeignKey("investigations.id", ondelete="SET NULL"), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    severity = Column(String(32), nullable=False, default="high", index=True)  # low, medium, high, critical
    risk_score = Column(Integer, default=60, index=True)
    status = Column(String(32), default="OPEN", index=True)                    # OPEN, INVESTIGATING, CONTAINED, RECOVERY, CLOSED
    summary = Column(Text, nullable=True)
    root_cause = Column(Text, nullable=True)
    affected_entities = Column(JSON, default=list)
    response_actions = Column(JSON, default=list)
    resolution = Column(Text, nullable=True)
    assigned_to = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
