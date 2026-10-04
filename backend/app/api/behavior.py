from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List

from app.database.database import get_db
from app.models.behavior import BehaviorProfile, Anomaly
from app.schemas.behavior import BehaviorProfileResponse, AnomalyResponse
from app.services.behavior import behavior_engine

router = APIRouter(prefix="/behavior", tags=["Behavior Analytics"])


@router.get("/profiles/{entity_id:path}", response_model=BehaviorProfileResponse)
async def get_behavior_profile(entity_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieves or builds baseline behavioral profile for a user or host."""
    ptype = "host" if entity_id.startswith("host:") else "user"
    prof = await behavior_engine.build_or_update_profile(db, entity_id, profile_type=ptype)
    return prof


@router.get("/anomalies", response_model=List[AnomalyResponse])
async def list_anomalies(
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db)
):
    """Lists statistical anomalies detected across all endpoints."""
    stmt = select(Anomaly).order_by(desc(Anomaly.detected_at)).limit(limit)
    res = await db.execute(stmt)
    return res.scalars().all()
