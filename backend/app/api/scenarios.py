from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from pydantic import BaseModel

from app.database.database import get_db
from app.services.scenario_runner import scenario_runner

router = APIRouter(prefix="/scenarios", tags=["Scenarios & Training"])


class TrainingSubmission(BaseModel):
    suspect_entity: str
    initial_access_method: str
    attack_chain_tactic: str
    evidence_justification: str


@router.get("")
async def list_scenarios():
    """Lists all available safe synthetic attack-chain simulation scenarios."""
    return scenario_runner.list_scenarios()


@router.post("/{scenario_id}/run")
async def run_scenario(scenario_id: str, db: AsyncSession = Depends(get_db)):
    """Executes synthetic scenario, fires detections, and generates attack chain investigation."""
    try:
        return await scenario_runner.run_scenario(db, scenario_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{scenario_id}/training_submit")
async def submit_training_answers(scenario_id: str, payload: TrainingSubmission):
    """Blue Team Training Mode - Evaluates analyst reasoning path and computes training score."""
    score = 0
    feedback = []

    # Scoring heuristic based on reasoning alignment
    if "user" in payload.suspect_entity.lower() or "ip" in payload.suspect_entity.lower() or "198." in payload.suspect_entity:
        score += 30
        feedback.append("Correct identification of primary adversary/pivot entity.")
    else:
        feedback.append("Consider investigating the originating external IP or authentication target.")

    if any(t in payload.initial_access_method.lower() for t in ["brute force", "login", "credential", "auth"]):
        score += 30
        feedback.append("Accurate assessment of Initial Access vector.")
    else:
        feedback.append("Initial events exhibit authentication anomalies consistent with credential abuse.")

    if len(payload.evidence_justification.strip()) > 15:
        score += 40
        feedback.append("Comprehensive forensic evidence justification provided.")
    else:
        feedback.append("Include specific Event IDs or process execution records to strengthen case evidence.")

    return {
        "scenario_id": scenario_id,
        "score": score,
        "max_score": 100,
        "grade": "Pass" if score >= 70 else "Needs Review",
        "reasoning_feedback": feedback,
        "notice": "Training score is for internal skill development and does not constitute a formal certification."
    }
