from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.ai.prompts import GUARDRAIL_SYSTEM_PROMPT
from app.ai.retrieval import retrieval_engine
from app.ai.provider import get_ai_provider

logger = logging.getLogger("specter.ai.assistant")


class GroundedInvestigationAssistant:
    """Grounded security reasoning assistant orchestrating retrieval, guardrails, and citation generation."""

    def __init__(self):
        self.provider = get_ai_provider()

    async def investigate(self, session: AsyncSession, investigation_id: str, question: str) -> Dict[str, Any]:
        # 1. Retrieve Investigation Telemetry & Evidence
        context = await retrieval_engine.retrieve_context(session, investigation_id)
        if not context.get("available", False):
            return {
                "answer": "Insufficient evidence in the current investigation. Investigation case was not found.",
                "cited_evidence": [],
                "grounded": False
            }

        # 2. Invoke Grounded AI Provider with Guardrails
        answer = await self.provider.generate_response(
            system_prompt=GUARDRAIL_SYSTEM_PROMPT,
            user_prompt=question,
            context=context
        )

        # Extract cited IDs
        cited_evs = [e["id"] for e in context.get("events", []) if e["id"] in answer]
        cited_alts = [a["id"] for a in context.get("alerts", []) if a["id"] in answer]
        cited_evis = [evi["id"] for evi in context.get("evidence", []) if evi["id"] in answer]

        return {
            "answer": answer,
            "cited_events": cited_evs,
            "cited_alerts": cited_alts,
            "cited_evidence": cited_evis,
            "grounded": True,
            "total_citations": len(cited_evs) + len(cited_alts) + len(cited_evis)
        }


investigation_assistant = GroundedInvestigationAssistant()
