from sqlalchemy import Column, String, Float, DateTime, JSON
from datetime import datetime, timezone
import uuid
from app.database.database import Base


class IOC(Base):
    __tablename__ = "iocs"

    id = Column(String(64), primary_key=True, default=lambda: f"ioc-{uuid.uuid4().hex[:12]}")
    ioc_type = Column(String(32), nullable=False, index=True)  # ip, domain, url, hash, file, user
    value = Column(String(255), nullable=False, index=True)
    confidence = Column(Float, nullable=False, default=0.9)
    classification = Column(String(64), default="suspicious")  # malicious, suspicious, benign, scanner
    source = Column(String(128), default="local-threat-intel")
    first_seen = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_seen = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    metadata_json = Column(JSON, default=dict)
