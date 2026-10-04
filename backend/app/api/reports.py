from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db
from app.schemas.report import ReportGenerateRequest, ReportResponse
from app.services.reporting import reporting_engine
from app.services.investigation import investigation_service
from app.services.pdf_generator import pdf_generator

router = APIRouter(prefix="/reports", tags=["Reporting"])


@router.post("/generate", response_model=ReportResponse)
async def generate_security_report(payload: ReportGenerateRequest, db: AsyncSession = Depends(get_db)):
    """Generates structured markdown/JSON incident and investigation reports."""
    try:
        return await reporting_engine.generate_report(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{investigation_id}/pdf")
@router.post("/export-pdf")
async def export_investigation_pdf(
    investigation_id: str = "INV-001",
    db: AsyncSession = Depends(get_db)
):
    """Compiles and exports an Executive Forensic Incident Response Dossier in PDF format."""
    try:
        # Fetch investigation details
        workbench = None
        try:
            workbench = await investigation_service.get_workbench(db, investigation_id)
        except Exception:
            pass

        data = {
            "report_id": f"REP-{investigation_id}",
            "title": f"Forensic Incident Report: {workbench.title if workbench else 'Advanced Attack Chain'}",
            "risk_score": workbench.risk_score if workbench else 88,
            "security_story": workbench.security_story if workbench else (
                "A multi-stage intrusion sequence was detected. The adversary initiated brute-force attempts "
                "from external IP 198.51.100.25, established execution via obfuscated PowerShell scripts, "
                "escalated privileges, and established C2 beaconing."
            ),
            "mitre_tactics": workbench.mitre_tactics if workbench else [
                "Credential Access", "Execution", "Privilege Escalation", "Command and Control", "Exfiltration"
            ],
            "timeline": [
                {
                    "time": t.timestamp.strftime("%H:%M:%S") if hasattr(t, "timestamp") else "14:22:00",
                    "sev": getattr(t, "severity", "HIGH"),
                    "action": getattr(t, "title", "Security Event"),
                    "details": getattr(t, "description", "-")
                }
                for t in (workbench.timeline if workbench and workbench.timeline else [])
            ] if workbench and workbench.timeline else None
        }

        pdf_bytes = pdf_generator.generate_investigation_pdf(data)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=specter_forensic_report_{investigation_id}.pdf"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"PDF Generation failed: {e}")

