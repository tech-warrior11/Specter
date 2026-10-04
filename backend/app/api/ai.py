from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import List, Optional

from app.database.database import get_db
from app.ai.investigation_assistant import investigation_assistant

router = APIRouter(prefix="/ai", tags=["AI Copilot"])


class AIInvestigateRequest(BaseModel):
    investigation_id: str = Field(..., description="Active investigation identifier")
    question: str = Field(default="Analyze this investigation and summarize the observed attack sequence.", description="Analyst question")


class AIInvestigateResponse(BaseModel):
    answer: str
    cited_events: List[str]
    cited_alerts: List[str]
    cited_evidence: List[str]
    grounded: bool
    total_citations: int


@router.post("/investigate", response_model=AIInvestigateResponse)
async def investigate_with_ai(payload: AIInvestigateRequest, db: AsyncSession = Depends(get_db)):
    """Grounded AI reasoning copilot citing verifiable evidence and refusing hallucination."""
    result = await investigation_assistant.investigate(
        session=db,
        investigation_id=payload.investigation_id,
        question=payload.question
    )
    return result
