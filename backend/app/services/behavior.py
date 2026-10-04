from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
import math
import logging

from app.models.behavior import BehaviorProfile, Anomaly
from app.models.event import Event
from app.schemas.behavior import BehaviorProfileResponse, AnomalyResponse

logger = logging.getLogger("specter.services.behavior")


class BehaviorAnalyticsEngine:
    """Deterministic statistical behavioral profiling and anomaly detection engine."""

    @staticmethod
    async def build_or_update_profile(session: AsyncSession, entity_id: str, profile_type: str = "user") -> BehaviorProfile:
        stmt = select(BehaviorProfile).where(BehaviorProfile.entity_id == entity_id)
        res = await session.execute(stmt)
        profile = res.scalar_one_or_none()

        clean_name = entity_id.split(":", 1)[-1] if ":" in entity_id else entity_id

        # Fetch recent historical events for this entity
        if profile_type == "user":
            ev_stmt = select(Event).where(Event.user_identity == clean_name).limit(500)
        else:
            ev_stmt = select(Event).where(Event.host == clean_name.upper()).limit(500)

        ev_res = await session.execute(ev_stmt)
        events = ev_res.scalars().all()

        hours = [e.timestamp.hour for e in events]
        hosts = list(set([e.host for e in events if e.host]))
        ips = list(set([e.source_ip for e in events if e.source_ip]))
        procs = list(set([e.process_name for e in events if e.process_name]))

        common_hours = list(set(hours)) if hours else [8, 9, 10, 11, 12, 13, 14, 15, 16, 17]

        if not profile:
            profile = BehaviorProfile(
                entity_id=entity_id,
                profile_type=profile_type,
                normal_login_hours=common_hours,
                normal_hosts=hosts,
                normal_ips=ips,
                normal_processes=procs,
                avg_daily_events=float(len(events)),
                std_daily_events=1.5
            )
            session.add(profile)
        else:
            profile.normal_login_hours = common_hours
            profile.normal_hosts = hosts
            profile.normal_ips = ips
            profile.normal_processes = procs
            profile.avg_daily_events = float(len(events))
            profile.last_calculated = datetime.now(timezone.utc)

        await session.commit()
        await session.refresh(profile)
        return profile

    @staticmethod
    async def evaluate_anomalies(session: AsyncSession, event: Event) -> List[Anomaly]:
        anomalies: List[Anomaly] = []
        now = datetime.now(timezone.utc)

        # 1. User Time-of-Day Anomaly
        if event.user_identity:
            uid = f"user:{event.user_identity}"
            stmt = select(BehaviorProfile).where(BehaviorProfile.entity_id == uid)
            res = await session.execute(stmt)
            prof = res.scalar_one_or_none()

            if prof and prof.normal_login_hours:
                event_hour = event.timestamp.hour
                if event_hour not in prof.normal_login_hours:
                    ano = Anomaly(
                        entity_id=uid,
                        anomaly_type="time_of_day_deviation",
                        score=0.72,
                        explanation=(
                            f"Observed authentication for user '{event.user_identity}' at hour {event_hour}:00, "
                            f"which deviates from historical baseline profile."
                        ),
                        event_ids=[event.id]
                    )
                    session.add(ano)
                    anomalies.append(ano)

        # 2. Rare Process Anomaly on Host
        if event.host and event.process_name:
            hid = f"host:{event.host}"
            stmt = select(BehaviorProfile).where(BehaviorProfile.entity_id == hid)
            res = await session.execute(stmt)
            prof = res.scalar_one_or_none()

            if prof and prof.normal_processes:
                if event.process_name not in prof.normal_processes:
                    ano = Anomaly(
                        entity_id=hid,
                        anomaly_type="rare_process_execution",
                        score=0.81,
                        explanation=(
                            f"Host '{event.host}' executed rare binary '{event.process_name}' "
                            f"unseen in historical endpoint process baseline."
                        ),
                        event_ids=[event.id]
                    )
                    session.add(ano)
                    anomalies.append(ano)

        if anomalies:
            await session.commit()

        return anomalies


behavior_engine = BehaviorAnalyticsEngine()
