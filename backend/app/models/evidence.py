from sqlalchemy import Column, String, BigInteger, Text, DateTime, ForeignKey
from datetime import datetime, timezone
import uuid
from app.database.database import Base


class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(String(64), primary_key=True, default=lambda: f"evi-{uuid.uuid4().hex[:12]}")
    investigation_id = Column(String(64), ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False, index=True)
    evidence_type = Column(String(64), nullable=False)  # log_snippet, network_capture, memory_dump, text_note, file_hash
    source = Column(String(128), nullable=False)
    description = Column(Text, nullable=False)
    content_text = Column(Text, nullable=True)
    file_path = Column(String(255), nullable=True)
    sha256 = Column(String(64), nullable=False, index=True)
    size_bytes = Column(BigInteger, default=0)
    collector_user = Column(String(64), nullable=False)
    collected_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
