from sqlalchemy import Column, String, DateTime, Text, JSON
from datetime import datetime, timezone
import uuid
from app.database.database import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(String(64), primary_key=True, default=lambda: f"evt-{uuid.uuid4().hex[:12]}")
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    source = Column(String(64), nullable=False, index=True)
    event_type = Column(String(64), nullable=False, index=True)  # authentication, process, network, file, privilege
    action = Column(String(64), nullable=False, index=True)      # login_failed, process_created, outbound_connection
    user_identity = Column(String(128), nullable=True, index=True)
    host = Column(String(128), nullable=True, index=True)
    source_ip = Column(String(64), nullable=True, index=True)
    destination_ip = Column(String(64), nullable=True, index=True)
    domain = Column(String(255), nullable=True, index=True)
    url = Column(Text, nullable=True)
    process_name = Column(String(255), nullable=True, index=True)
    parent_process = Column(String(255), nullable=True)
    file_path = Column(Text, nullable=True)
    file_hash = Column(String(128), nullable=True, index=True)
    resource_id = Column(String(255), nullable=True, index=True)
    severity = Column(String(32), nullable=False, default="informational", index=True)  # informational, low, medium, high, critical
    raw_event = Column(JSON, nullable=False)
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
