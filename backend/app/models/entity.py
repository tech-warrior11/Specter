from sqlalchemy import Column, String, Float, Integer, DateTime, JSON, ForeignKey
from datetime import datetime, timezone
from app.database.database import Base


class Entity(Base):
    __tablename__ = "entities"

    id = Column(String(64), primary_key=True)  # e.g. ip:10.10.10.50, user:alice, host:LAB-PC-01
    entity_type = Column(String(32), nullable=False, index=True)  # USER, HOST, IP, DOMAIN, URL, PROCESS, FILE, HASH, RESOURCE
    value = Column(String(255), nullable=False, index=True)
    risk_score = Column(Float, default=0.0, index=True)
    criticality = Column(String(32), default="medium")  # low, medium, high, critical
    first_seen = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    last_seen = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class EntityRelationship(Base):
    __tablename__ = "entity_relationships"

    id = Column(String(64), primary_key=True)
    source_entity_id = Column(String(64), ForeignKey("entities.id", ondelete="CASCADE"), nullable=False, index=True)
    target_entity_id = Column(String(64), ForeignKey("entities.id", ondelete="CASCADE"), nullable=False, index=True)
    relation_type = Column(String(64), nullable=False, index=True)
    weight = Column(Integer, default=1)
    first_observed = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    last_observed = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    evidence_event_ids = Column(JSON, default=list)
