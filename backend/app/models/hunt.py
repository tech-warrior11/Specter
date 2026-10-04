from sqlalchemy import Column, String, Text, DateTime, JSON, ForeignKey
from datetime import datetime, timezone
import uuid
from app.database.database import Base


class HuntQuery(Base):
    __tablename__ = "hunt_queries"

    id = Column(String(64), primary_key=True, default=lambda: f"hunt-{uuid.uuid4().hex[:12]}")
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    query_dsl = Column(JSON, nullable=False)
    raw_query = Column(Text, nullable=False)
    created_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
