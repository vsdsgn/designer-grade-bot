import asyncio
import logging
import os
from typing import Any, Dict, List

from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas

logger = logging.getLogger("designer_grade_bot.pdf")


def _wrap_text(text: str, font_name: str, font_size: int, max_width: float) -> List[str]:
    words = text.split()
    if not words:
        return [""]

    lines: List[str] = []
    current = words[0]
    for word in words[1:]:
        test_line = f"{current} {word}"
        if stringWidth(test_line, font_name, font_size) <= max_width:
            current = test_line
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def _draw_lines(c: canvas.Canvas, lines: List[str], x: float, y: float, leading: int) -> float:
    for line in lines:
        c.drawString(x, y, line)
        y -= leading
        if y < 50:
            c.showPage()
            c.setFont("Helvetica", 11)
            y = A4[1] - 60
    return y


def _section(c: canvas.Canvas, title: str, y: float, margin: float) -> float:
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, title)
    return y - 16


def _build_pdf(report: Dict[str, Any], user_name: str, file_path: str) -> str:
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4
    margin = 50
    y = height - margin

    c.setFont("Helvetica-Bold", 16)
    c.drawString(margin, y, "Designer Grade Bot — Report")
    y -= 30

    c.setFont("Helvetica", 11)
    c.drawString(margin, y, f"User: {user_name}")
    y -= 18

    grade = report.get("grade", "Unknown")
    c.drawString(margin, y, f"Grade: {grade}")
    y -= 24

    summary = report.get("summary", "")
    if summary:
        y = _section(c, "Summary", y, margin)
        c.setFont("Helvetica", 11)
        lines = _wrap_text(summary, "Helvetica", 11, width - margin * 2)
        y = _draw_lines(c, lines, margin, y, 14)
        y -= 10

    strengths = report.get("strengths", [])
    if strengths:
        y = _section(c, "Strengths", y, margin)
        c.setFont("Helvetica", 11)
        for item in strengths:
            lines = _wrap_text(f"- {item}", "Helvetica", 11, width - margin * 2)
            y = _draw_lines(c, lines, margin, y, 14)
            y -= 4
        y -= 10

    weaknesses = report.get("weaknesses", [])
    if weaknesses:
        y = _section(c, "Growth Areas", y, margin)
        c.setFont("Helvetica", 11)
        for item in weaknesses:
            lines = _wrap_text(f"- {item}", "Helvetica", 11, width - margin * 2)
            y = _draw_lines(c, lines, margin, y, 14)
            y -= 4
        y -= 10

    detailed_report = report.get("detailed_report", "")
    if detailed_report:
        y = _section(c, "Detailed Report", y, margin)
        c.setFont("Helvetica", 11)
        lines = _wrap_text(detailed_report, "Helvetica", 11, width - margin * 2)
        y = _draw_lines(c, lines, margin, y, 14)
        y -= 10

    recommendations = report.get("recommendations", [])
    if recommendations:
        y = _section(c, "Recommendations", y, margin)
        c.setFont("Helvetica", 11)
        for item in recommendations:
            lines = _wrap_text(f"- {item}", "Helvetica", 11, width - margin * 2)
            y = _draw_lines(c, lines, margin, y, 14)
            y -= 4
        y -= 10

    materials = report.get("materials", [])
    if materials:
        y = _section(c, "Materials", y, margin)
        c.setFont("Helvetica", 11)
        for item in materials:
            title = item.get("title") if isinstance(item, dict) else str(item)
            url = item.get("url") if isinstance(item, dict) else ""
            line = f"- {title}"
            if url:
                line += f" ({url})"
            lines = _wrap_text(line, "Helvetica", 11, width - margin * 2)
            y = _draw_lines(c, lines, margin, y, 14)
            y -= 4

    c.showPage()
    c.save()
    return file_path


async def generate_pdf_report(report: Dict[str, Any], user_name: str, file_path: str) -> str:
    try:
        return await asyncio.to_thread(_build_pdf, report, user_name, file_path)
    except Exception:
        logger.exception("Failed to generate PDF report")
        return ""
