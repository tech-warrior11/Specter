from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, List

from app.database.database import get_db
from app.models.detection_rule import DetectionRule
from app.models.alert import Alert
from app.schemas.mitre import MITREMatrixResponse, MITRETacticCoverage, MITRETechnique
from app.services.detection import detection_engine

router = APIRouter(prefix="/mitre", tags=["MITRE ATT&CK"])


@router.get("/coverage", response_model=MITREMatrixResponse)
async def get_mitre_coverage_matrix(db: AsyncSession = Depends(get_db)):
    """Computes dynamic MITRE ATT&CK matrix coverage and alert triggers."""
    await detection_engine.sync_rules_to_db(db)

    rules_res = await db.execute(select(DetectionRule))
    rules = rules_res.scalars().all()

    alerts_res = await db.execute(select(Alert))
    alerts = alerts_res.scalars().all()

    # Map tactics to techniques
    tactics_map: Dict[str, Dict[str, Dict[str, Any]]] = {}

    for r in rules:
        tactic = r.mitre_tactic or "Other"
        tech_id = r.mitre_technique_id or "T_CUSTOM"
        tech_name = r.mitre_technique_name or r.name

        if tactic not in tactics_map:
            tactics_map[tactic] = {}

        if tech_id not in tactics_map[tactic]:
            tactics_map[tactic][tech_id] = {
                "id": tech_id,
                "name": tech_name,
                "tactic": tactic,
                "description": r.description,
                "detection_count": 0,
                "alerts_triggered_count": 0
            }
        tactics_map[tactic][tech_id]["detection_count"] += 1

    # Count alert triggers
    for a in alerts:
        if a.mitre_tactic and a.mitre_tactic in tactics_map:
            for tech_id in tactics_map[a.mitre_tactic]:
                if tech_id in (a.mitre_technique or ""):
                    tactics_map[a.mitre_tactic][tech_id]["alerts_triggered_count"] += 1

    coverage_tactics: List[MITRETacticCoverage] = []
    total_techs = 0

    for tactic, techs in tactics_map.items():
        tech_list = [MITRETechnique(**data) for data in techs.values()]
        total_techs += len(tech_list)
        coverage_tactics.append(MITRETacticCoverage(
            tactic=tactic,
            techniques_covered_count=len(tech_list),
            total_detections=sum(t.detection_count for t in tech_list),
            techniques=tech_list
        ))

    return MITREMatrixResponse(
        tactics=coverage_tactics,
        total_coverage_techniques=total_techs,
        total_active_detections=len(rules)
    )
