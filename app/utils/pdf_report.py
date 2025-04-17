
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import uuid
import os

def generate_pdf_report(username, grade, recommendations, materials):
    filename = f"{username}_report_{uuid.uuid4().hex[:6]}.pdf"
    file_path = f"/tmp/{filename}"

    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, f"👤 Пользователь: {username}")
    c.drawString(50, height - 80, f"📊 Грейд: {grade}")

    c.setFont("Helvetica", 12)
    y = height - 120
    c.drawString(50, y, "📌 Рекомендации:")
    for line in recommendations.split("\n"):
        y -= 20
        c.drawString(60, y, line)

    y -= 40
    c.drawString(50, y, "🎓 Полезные материалы:")
    for line in materials.split("\n"):
        y -= 20
        if y < 100:
            c.showPage()
            y = height - 50
        c.drawString(60, y, line)

    c.showPage()
    c.save()

    return file_path
