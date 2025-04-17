import os
from datetime import datetime

FEEDBACK_PATH = "data_storage/feedback.txt"
os.makedirs(os.path.dirname(FEEDBACK_PATH), exist_ok=True)

def save_feedback(chat_id, text):
    try:
        with open(FEEDBACK_PATH, "a", encoding="utf-8") as f:
            f.write(f"Time: {datetime.now().isoformat()}\n")
            f.write(f"From {chat_id}: {text}\n")
            f.write(f"{'-'*40}\n")
        print(f"💬 Отзыв сохранён от {chat_id}")
    except Exception as e:
        print(f"⚠️ Ошибка при сохранении отзыва: {e}")