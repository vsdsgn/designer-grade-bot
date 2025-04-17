
import os
from datetime import datetime

FEEDBACK_PATH = "feedback.txt"

def save_feedback(chat_id, text):
    try:
        with open(FEEDBACK_PATH, "a", encoding="utf-8") as f:
            f.write(f"Time: {datetime.now().isoformat()}\n")
            f.write(f"From {chat_id}: {text}\n")
            f.write(f"{'-'*40}\n")
    except Exception as e:
        print(f"❌ Ошибка при сохранении фидбека от {chat_id}:", e)
