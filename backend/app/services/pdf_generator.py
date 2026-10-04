import io
from typing import Dict, Any, List
from datetime import datetime, timezone
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


class ForensicPDFGenerator:
    """Enterprise Forensic PDF Report Compiler.
    Produces high-fidelity SOC Investigation & Incident Response PDF Documents.
    """

    @staticmethod
    def generate_investigation_pdf(data: Dict[str, Any]) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        
        # Custom Brand Styles
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#0f172a"),
            alignment=TA_LEFT
        )

        subtitle_style = ParagraphStyle(
            'ReportSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=11,
            leading=15,
            textColor=colors.HexColor("#0284c7")
        )

        heading2_style = ParagraphStyle(
            'Heading2',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=13,
            leading=17,
            textColor=colors.HexColor("#0f172a"),
            spaceBefore=12,
            spaceAfter=6
        )

        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9.5,
            leading=13.5,
            textColor=colors.HexColor("#334155")
        )

        callout_style = ParagraphStyle(
            'Callout',
            parent=styles['Normal'],
            fontName='Helvetica-Oblique',
            fontSize=9.5,
            leading=13.5,
            textColor=colors.HexColor("#1e293b")
        )

        table_header_style = ParagraphStyle(
            'TableHeader',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=9,
            leading=11,
            textColor=colors.white
        )

        table_cell_style = ParagraphStyle(
            'TableCell',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor("#1e293b")
        )

        story = []

        # 1. Header Banner
        story.append(Paragraph("Specter X | FORENSIC INCIDENT DOSSIER", subtitle_style))
        story.append(Spacer(1, 4))
        story.append(Paragraph(data.get("title", "Forensic Investigation Report"), title_style))
        story.append(Spacer(1, 8))

        # Metadata Table
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        meta_data = [
            [
                Paragraph("<b>Report ID:</b> " + data.get("report_id", "REP-001"), table_cell_style),
                Paragraph("<b>Generated:</b> " + now_str, table_cell_style)
            ],
            [
                Paragraph("<b>Classification:</b> RESTRICTED DEFENSIVE LAB", table_cell_style),
                Paragraph("<b>Risk Score:</b> " + f"<b>{data.get('risk_score', 85)}/100 (HIGH SEVERITY)</b>", table_cell_style)
            ]
        ]
        meta_table = Table(meta_data, colWidths=[270, 270])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 14))

        # 2. Executive Attack Summary
        story.append(Paragraph("1. Executive Attack Narrative & Root Cause Analysis", heading2_style))
        story_text = data.get("security_story", "A multi-stage intrusion sequence was detected and correlated across the enterprise topology.")
        story.append(Paragraph(story_text.replace("\n", "<br/>"), body_style))
        story.append(Spacer(1, 12))

        # 3. Key Findings & MITRE ATT&CK Mapping
        story.append(Paragraph("2. MITRE ATT&CK Tactics & Observed Threat Matrix", heading2_style))
        tactics = data.get("mitre_tactics") or ["Initial Access", "Execution", "Privilege Escalation", "Collection", "Command and Control", "Exfiltration"]
        tactic_cells = [[Paragraph(f"• <b>{t}</b>", table_cell_style)] for t in tactics]
        tactic_table = Table(tactic_cells, colWidths=[540])
        tactic_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f0fdf4")),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#86efac")),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(tactic_table)
        story.append(Spacer(1, 14))

        # 4. Chronological Forensic Timeline
        story.append(Paragraph("3. Forensic Event Chronology", heading2_style))
        timeline_rows = [
            [
                Paragraph("Time (UTC)", table_header_style),
                Paragraph("Severity", table_header_style),
                Paragraph("Tactic / Action", table_header_style),
                Paragraph("Evidence Details", table_header_style)
            ]
        ]
        
        timeline_events = data.get("timeline") or [
            {"time": "14:22:01", "sev": "HIGH", "action": "Brute Force Authentication", "details": "5 repeated failed logins against testuser from 198.51.100.25"},
            {"time": "14:22:15", "sev": "CRITICAL", "action": "Obfuscated PowerShell Execution", "details": "Encoded script spawn: powershell.exe -enc SQBFAFgA..."},
            {"time": "14:23:00", "sev": "HIGH", "action": "Privilege Elevation", "details": "Security token assigned to user:testuser on host LAB-PC-01"},
            {"time": "14:24:12", "sev": "CRITICAL", "action": "C2 Beaconing Egress", "details": "Outbound HTTP stream to 198.51.100.25 on port 443"}
        ]

        for ev in timeline_events:
            sev = ev.get("sev", "HIGH").upper()
            sev_color = "#dc2626" if sev == "CRITICAL" else ("#ea580c" if sev == "HIGH" else "#ca8a04")
            timeline_rows.append([
                Paragraph(ev.get("time", "12:00:00"), table_cell_style),
                Paragraph(f"<font color='{sev_color}'><b>{sev}</b></font>", table_cell_style),
                Paragraph(ev.get("action", "Security Event"), table_cell_style),
                Paragraph(ev.get("details", "-"), table_cell_style)
            ])

        timeline_table = Table(timeline_rows, colWidths=[65, 60, 150, 265])
        timeline_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0f172a")),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")])
        ]))
        story.append(timeline_table)
        story.append(Spacer(1, 14))

        # 5. SOAR Containment & Remediation Actions
        story.append(Paragraph("4. Recommended SOAR Containment & Hardening Playbook", heading2_style))
        remediation_text = (
            "1. <b>Isolate Host Endpoint:</b> Quarantine LAB-PC-01 immediately to halt lateral pivoting.<br/>"
            "2. <b>Edge Perimeter IP Block:</b> Deploy drop rules for adversary IP 198.51.100.25.<br/>"
            "3. <b>Revoke & Reset Credentials:</b> Invalidate all active Kerberos / JWT sessions for user:testuser.<br/>"
            "4. <b>Cryptographic Evidence Archival:</b> Retain SHA-256 evidence vault objects for legal chain-of-custody."
        )
        remed_table = Table([[Paragraph(remediation_text, table_cell_style)]], colWidths=[540])
        remed_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#eff6ff")),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#93c5fd")),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(remed_table)

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()


pdf_generator = ForensicPDFGenerator()
