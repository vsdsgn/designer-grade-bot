
import uuid
import re
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def generate_pdf_report(username, grade, recommendations, materials):
    try:
        safe_username = re.sub(r"[^\w\d_-]", "_", username)
        filename = f"{safe_username}_report_{uuid.uuid4().hex[:6]}.pdf"
        file_path = os.path.join("reports", filename)

        os.makedirs("reports", exist_ok=True)

        c = canvas.Canvas(file_path, pagesize=A4)
        width, height = A4

        y = height - 50
        c.drawString(50, y, f"👤 Пользователь: {username}")
        y -= 30
        c.drawString(50, y, f"📊 Грейд: {grade}")
        y -= 50

        c.drawString(50, y, "📌 Рекомендации:")
        y -= 30
        for line in recommendations:
            c.drawString(60, y, line)
            y -= 20

        y -= 30
        c.drawString(50, y, "🎓 Полезные материалы:")
        y -= 30
        for line in materials:
            c.drawString(60, y, line)
            y -= 20

        c.save()
        return file_path
    except Exception as e:
        print("❌ Ошибка при генерации PDF:", e)
        return None
