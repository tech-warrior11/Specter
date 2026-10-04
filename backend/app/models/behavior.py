from sqlalchemy import Column, String, Float, Text, DateTime, JSON, ForeignKey
from datetime import datetime, timezone
import uuid
from app.database.database import Base


class BehaviorProfile(Base):
    __tablename__ = "behavior_profiles"

    id = Column(String(64), primary_key=True, default=lambda: f"prof-{uuid.uuid4().hex[:12]}")
    entity_id = Column(String(64), ForeignKey("entities.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    profile_type = Column(String(32), nullable=False)  # user, host
    normal_login_hours = Column(JSON, default=list)
    normal_hosts = Column(JSON, default=list)
    normal_ips = Column(JSON, default=list)
    normal_processes = Column(JSON, default=list)
    avg_daily_events = Column(Float, default=0.0)
    std_daily_events = Column(Float, default=0.0)
    last_calculated = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Anomaly(Base):
    __tablename__ = "anomalies"

    id = Column(String(64), primary_key=True, default=lambda: f"ano-{uuid.uuid4().hex[:12]}")
    entity_id = Column(String(64), ForeignKey("entities.id", ondelete="CASCADE"), nullable=False, index=True)
    anomaly_type = Column(String(64), nullable=False, index=True)  # frequency_deviation, time_of_day, rare_process, new_entity
    score = Column(Float, nullable=False)
    explanation = Column(Text, nullable=False)
    event_ids = Column(JSON, default=list)
    detected_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
