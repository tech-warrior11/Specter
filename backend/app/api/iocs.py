from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional

from app.database.database import get_db
from app.models.ioc import IOC
from app.schemas.ioc import IOCResponse, IOCCreate, IOCLookupRequest, IOCMatch
from app.services.threat_intel import threat_intel

router = APIRouter(prefix="/iocs", tags=["Threat Intelligence"])


@router.get("", response_model=List[IOCResponse])
async def list_iocs(
    ioc_type: Optional[str] = None,
    classification: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Lists local threat intelligence indicators of compromise."""
    await threat_intel.seed_default_iocs(db)
    query = select(IOC).order_by(desc(IOC.last_seen))
    if ioc_type:
        query = query.where(IOC.ioc_type == ioc_type.lower())
    if classification:
        query = query.where(IOC.classification == classification.lower())

    res = await db.execute(query)
    return res.scalars().all()


@router.post("/lookup", response_model=List[IOCMatch])
async def lookup_iocs(payload: IOCLookupRequest, db: AsyncSession = Depends(get_db)):
    """Fast batch lookup against local synthetic threat intelligence database."""
    await threat_intel.seed_default_iocs(db)
    return await threat_intel.lookup(db, payload.values)


@router.post("/live-lookup")
async def live_ioc_lookup(
    value: str = Query(..., description="IP, Domain, URL, or Hash to check in real-time"),
    ioc_type: Optional[str] = Query(None, description="Optional type (ip, domain, hash, url)")
):
    """Performs real-time reputation analysis querying AbuseIPDB, AlienVault OTX, URLhaus & CISA feeds."""
    return await threat_intel.perform_live_lookup(value=value, ioc_type=ioc_type)


@router.post("/sync-feeds")
async def sync_live_feeds(
    feed_name: str = Query("ALL", description="Feed provider to sync: AbuseIPDB, AlienVault, URLhaus, CISA, ALL"),
    db: AsyncSession = Depends(get_db)
):
    """Fetches and synchronizes live community CTI threat intelligence feeds into the database."""
    return await threat_intel.sync_community_feeds(session=db, feed_name=feed_name)

