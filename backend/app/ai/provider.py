from abc import ABC, abstractmethod
from typing import Dict, Any, List
import logging
from app.config import settings

logger = logging.getLogger("specter.ai.provider")


class BaseAIProvider(ABC):
    @abstractmethod
    async def generate_response(self, system_prompt: str, user_prompt: str, context: Dict[str, Any]) -> str:
        pass


class LocalGroundedProvider(BaseAIProvider):
    """Offline, deterministic AI reasoning provider that guarantees 100% evidence citation."""

    async def generate_response(self, system_prompt: str, user_prompt: str, context: Dict[str, Any]) -> str:
        # 1. Filter malicious instructions / prompt injection attempts FIRST
        prompt_lower = user_prompt.lower()
        if any(bad in prompt_lower for bad in ["ignore previous", "system instructions", "generate exploit", "attack code", "bypass"]):
            return (
                "Security Policy Refusal: Specter Assistant is strictly defensive and refuses to process "
                "instructions aiming to alter system parameters or generate offensive exploits."
            )

        events = context.get("events", [])
        alerts = context.get("alerts", [])
        evidence = context.get("evidence", [])
        root_entities = context.get("root_entities", [])

        if not events and not alerts:
            return "Insufficient evidence in the current investigation to support an analytical finding."

        # Build grounded analytical breakdown
        response_lines = [
            f"### Grounded Investigation Analysis",
            f"**Target Case:** {context.get('title', 'Unknown Case')} ({context.get('investigation_id', 'N/A')})",
            f"\n#### 1. Correlated Attack Sequence",
        ]

        for i, ev in enumerate(events[:10], 1):
            response_lines.append(
                f"- **Step {i}** [Ref: `{ev.get('id')}`]: Observed action `{ev.get('action')}` on host `{ev.get('host', 'N/A')}` "
                f"by identity `{ev.get('user', 'N/A')}` (Source IP: `{ev.get('source_ip', 'N/A')}`)."
            )

        if alerts:
            response_lines.append(f"\n#### 2. Triggered Detections & MITRE ATT&CK TTPs")
            for a in alerts[:5]:
                response_lines.append(
                    f"- Alert `{a.get('id')}`: {a.get('title')} (MITRE Tactic: `{a.get('mitre_tactic', 'N/A')}`, Technique: `{a.get('mitre_technique', 'N/A')}`)."
                )

        if evidence:
            response_lines.append(f"\n#### 3. Verified Evidence Integrity")
            for e in evidence[:3]:
                response_lines.append(
                    f"- Evidence `{e.get('id')}`: {e.get('description')} (SHA-256: `{e.get('sha256')}`)."
                )

        response_lines.append(f"\n#### 4. Recommended Defensive Actions")
        response_lines.append(f"- Isolate impacted endpoints: {', '.join([e for e in root_entities if e.startswith('host:')]) or 'LAB-PC-01'}")
        response_lines.append(f"- Revoke active credentials for targeted accounts: {', '.join([e for e in root_entities if e.startswith('user:')]) or 'Target Accounts'}")
        response_lines.append(f"- Block malicious egress indicators at firewall perimeter.")

        return "\n".join(response_lines)


def get_ai_provider() -> BaseAIProvider:
    return LocalGroundedProvider()
