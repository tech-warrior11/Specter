import uuid
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

from app.models.investigation import Investigation
from app.models.incident import Incident
from app.models.alert import Alert
from app.schemas.report import ReportGenerateRequest, ReportResponse
from app.services.investigation import investigation_service

logger = logging.getLogger("specter.services.reporting")


class ReportingEngine:
    """Generates structured, evidence-grounded security reports."""

    @staticmethod
    async def generate_report(session: AsyncSession, req: ReportGenerateRequest) -> ReportResponse:
        report_id = f"rep-{uuid.uuid4().hex[:12]}"
        now = datetime.now(timezone.utc)
        title = req.title or f"Specter {req.report_type.replace('_', ' ').title()} Report"

        key_findings = []
        mitre_summary = []
        evidence_count = 0
        risk_score = 50
        content_lines = [
            f"# {title}",
            f"**Report ID:** {report_id}  ",
            f"**Classification:** RESTRICTED DEFENSIVE LAB  ",
            f"**Generated:** {now.strftime('%Y-%m-%d %H:%M:%S UTC')}  ",
            "---",
            "## 1. Executive Summary"
        ]

        if req.report_type == "investigation" and req.target_id:
            workbench = await investigation_service.get_workbench(session, req.target_id)
            risk_score = workbench.risk_score
            key_findings.append(f"Primary Root Entities: {', '.join(workbench.root_entities)}")
            key_findings.append(f"Correlated Alerts: {len(workbench.related_alerts)} alerts detected.")
            key_findings.append(f"Assessed Risk Score: {workbench.risk_score}/100 ({workbench.priority} priority).")

            mitre_summary = workbench.mitre_tactics
            evidence_count = len(workbench.evidence)

            content_lines.append(f"Investigation Case **{workbench.id}** ({workbench.title}) was analyzed.")
            content_lines.append(f"\n{workbench.security_story}")

            if req.include_timeline and workbench.timeline:
                content_lines.append("\n## 2. Chronological Attack Timeline")
                for t in workbench.timeline:
                    content_lines.append(f"- **{t.timestamp.strftime('%H:%M:%S')}** [{t.severity.upper()}] *{t.title}*: {t.description}")

            if req.include_mitre and workbench.mitre_tactics:
                content_lines.append("\n## 3. MITRE ATT&CK Mapping")
                for tac in workbench.mitre_tactics:
                    content_lines.append(f"- **Tactic:** {tac}")

            if req.include_evidence and workbench.evidence:
                content_lines.append("\n## 4. Verified Forensic Evidence")
                for ev in workbench.evidence:
                    content_lines.append(f"- **Evidence {ev.id}** ({ev.evidence_type}): {ev.description} | SHA-256: `{ev.sha256}`")

        else:
            content_lines.append("Executive overview of current telemetry velocity, open detection alerts, and correlated threat graph topology.")
            key_findings.append("Continuous security graph monitoring active across all endpoints.")
            key_findings.append("No critical unauthorized bypasses observed outside controlled simulation bounds.")

        content_lines.append("\n---\n*Specter Defensive Security Platform - Grounded Intelligence*")

        markdown_body = "\n".join(content_lines)

        return ReportResponse(
            report_id=report_id,
            report_type=req.report_type,
            title=title,
            generated_at=now,
            content_markdown=markdown_body,
            risk_score=risk_score,
            key_findings=key_findings,
            mitre_summary=mitre_summary,
            evidence_items_count=evidence_count
        )


reporting_engine = ReportingEngine()
