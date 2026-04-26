"""
SANDY AI - Report Generator
Produces PDF security reports from AnalysisResult objects
"""

import json
import os
from datetime import datetime
from typing import Optional

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.colors import HexColor, black, white
    from reportlab.lib.units import cm
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                     Table, TableStyle, HRFlowable)
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


# ── Colour palette ────────────────────────────────────────────────────────────
C_BG        = HexColor("#0d1117") if REPORTLAB_AVAILABLE else None
C_PANEL     = HexColor("#161b22") if REPORTLAB_AVAILABLE else None
C_ACCENT    = HexColor("#00ff88") if REPORTLAB_AVAILABLE else None
C_RED       = HexColor("#ff2d55") if REPORTLAB_AVAILABLE else None
C_ORANGE    = HexColor("#ff6b35") if REPORTLAB_AVAILABLE else None
C_YELLOW    = HexColor("#ffd60a") if REPORTLAB_AVAILABLE else None
C_GREEN     = HexColor("#30d158") if REPORTLAB_AVAILABLE else None
C_BLUE      = HexColor("#0a84ff") if REPORTLAB_AVAILABLE else None
C_TEXT      = HexColor("#c9d1d9") if REPORTLAB_AVAILABLE else None
C_SUBTLE    = HexColor("#8b949e") if REPORTLAB_AVAILABLE else None

SEV_COLOR = {
    "CRITICAL": C_RED,
    "HIGH":     C_ORANGE,
    "MEDIUM":   C_YELLOW,
    "LOW":      C_GREEN,
    "INFO":     C_BLUE,
    "CLEAN":    C_GREEN,
}


def _severity_color(sev: str):
    return SEV_COLOR.get(sev, C_BLUE)


def generate_pdf_report(analysis, output_path: Optional[str] = None) -> str:
    """
    Generate a styled PDF report.
    Returns the path to the generated file.
    """
    if not REPORTLAB_AVAILABLE:
        raise ImportError("reportlab not installed. Run: pip install reportlab")

    if output_path is None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs("reports/output", exist_ok=True)
        output_path = f"reports/output/SANDY_Report_{ts}.pdf"

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
        title="SANDY AI Security Report",
    )

    styles = getSampleStyleSheet()
    story = []

    # ── Header ────────────────────────────────────────────────────────────────
    title_style = ParagraphStyle(
        "Title", parent=styles["Heading1"],
        fontSize=26, textColor=C_ACCENT,
        spaceAfter=4, fontName="Courier-Bold", alignment=TA_CENTER,
    )
    sub_style = ParagraphStyle(
        "Sub", parent=styles["Normal"],
        fontSize=11, textColor=C_SUBTLE,
        spaceAfter=2, fontName="Courier", alignment=TA_CENTER,
    )

    story.append(Paragraph("🛡️  SANDY AI", title_style))
    story.append(Paragraph("Security Assessment Report", sub_style))
    story.append(Paragraph(
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        sub_style,
    ))
    story.append(HRFlowable(width="100%", thickness=1, color=C_ACCENT,
                             spaceAfter=12))

    # ── Meta info ─────────────────────────────────────────────────────────────
    info_style = ParagraphStyle(
        "Info", parent=styles["Normal"],
        fontSize=10, textColor=C_TEXT, fontName="Courier",
        spaceAfter=6,
    )
    head_style = ParagraphStyle(
        "Head", parent=styles["Heading2"],
        fontSize=13, textColor=C_ACCENT,
        fontName="Courier-Bold", spaceAfter=6,
    )

    story.append(Paragraph("SCAN DETAILS", head_style))
    story.append(Paragraph(f"<b>Tool:</b>   {analysis.tool.upper()}", info_style))
    story.append(Paragraph(f"<b>Target:</b> {analysis.target}", info_style))
    story.append(Spacer(1, 8))

    # ── Risk badge ────────────────────────────────────────────────────────────
    risk_color = _severity_color(analysis.risk_level)
    risk_data = [[f"  RISK LEVEL: {analysis.risk_level}  "]]
    risk_table = Table(risk_data, hAlign="LEFT")
    risk_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), risk_color),
        ("TEXTCOLOR",  (0, 0), (-1, -1), black),
        ("FONTNAME",   (0, 0), (-1, -1), "Courier-Bold"),
        ("FONTSIZE",   (0, 0), (-1, -1), 14),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [risk_color]),
        ("BOX",        (0, 0), (-1, -1), 1, black),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
    ]))
    story.append(risk_table)
    story.append(Spacer(1, 8))
    story.append(Paragraph(f"<i>{analysis.summary}</i>", info_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=C_SUBTLE,
                             spaceBefore=8, spaceAfter=12))

    # ── Open ports ───────────────────────────────────────────────────────────
    if analysis.open_ports:
        story.append(Paragraph("OPEN PORTS", head_style))
        for svc in analysis.services:
            story.append(Paragraph(f"  • {svc}", info_style))
        story.append(Spacer(1, 8))
        if analysis.os_guess:
            story.append(Paragraph(
                f"<b>OS Detected:</b> {analysis.os_guess}", info_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=C_SUBTLE,
                                 spaceBefore=8, spaceAfter=12))

    # ── Findings table ────────────────────────────────────────────────────────
    if analysis.findings:
        story.append(Paragraph("FINDINGS", head_style))

        tdata = [["SEVERITY", "TITLE", "DESCRIPTION", "RECOMMENDATION"]]
        for f in analysis.findings:
            tdata.append([f.severity, f.title, f.description[:60], f.recommendation[:60]])

        col_widths = [2.2*cm, 4*cm, 6*cm, 5*cm]
        t = Table(tdata, colWidths=col_widths, repeatRows=1)

        ts_style = [
            ("BACKGROUND",  (0, 0), (-1, 0),  HexColor("#21262d")),
            ("TEXTCOLOR",   (0, 0), (-1, 0),  C_ACCENT),
            ("FONTNAME",    (0, 0), (-1, 0),  "Courier-Bold"),
            ("FONTSIZE",    (0, 0), (-1, -1), 8),
            ("FONTNAME",    (0, 1), (-1, -1), "Courier"),
            ("TEXTCOLOR",   (0, 1), (-1, -1), C_TEXT),
            ("BACKGROUND",  (0, 1), (-1, -1), HexColor("#161b22")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1),
             [HexColor("#161b22"), HexColor("#1c2128")]),
            ("GRID",        (0, 0), (-1, -1), 0.4, HexColor("#30363d")),
            ("TOPPADDING",    (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING",   (0, 0), (-1, -1), 5),
        ]

        # Colour severity column cells
        sev_map = {
            "CRITICAL": C_RED, "HIGH": C_ORANGE,
            "MEDIUM": C_YELLOW, "LOW": C_GREEN, "INFO": C_BLUE,
        }
        for i, f in enumerate(analysis.findings, start=1):
            c = sev_map.get(f.severity, C_TEXT)
            ts_style.append(("TEXTCOLOR", (0, i), (0, i), c))

        t.setStyle(TableStyle(ts_style))
        story.append(t)
        story.append(Spacer(1, 16))

    # ── Raw output snippet ────────────────────────────────────────────────────
    story.append(Paragraph("RAW OUTPUT (truncated)", head_style))
    raw_style = ParagraphStyle(
        "Raw", parent=styles["Code"],
        fontSize=7, textColor=C_SUBTLE,
        fontName="Courier", leading=9,
    )
    raw_text = (analysis.raw_truncated[:1500]
                .replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
    story.append(Paragraph(raw_text or "(no output)", raw_style))

    doc.build(story)
    return output_path


def generate_json_report(analysis, output_path: Optional[str] = None) -> str:
    if output_path is None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs("reports/output", exist_ok=True)
        output_path = f"reports/output/SANDY_Report_{ts}.json"

    report = {
        "generated_at": datetime.now().isoformat(),
        "tool": analysis.tool,
        "target": analysis.target,
        "risk_level": analysis.risk_level,
        "summary": analysis.summary,
        "open_ports": analysis.open_ports,
        "services": analysis.services,
        "os_guess": analysis.os_guess,
        "findings": [
            {
                "severity": f.severity,
                "title": f.title,
                "description": f.description,
                "recommendation": f.recommendation,
            }
            for f in analysis.findings
        ],
    }

    with open(output_path, "w") as fp:
        json.dump(report, fp, indent=2)

    return output_path
