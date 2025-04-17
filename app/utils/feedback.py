
import os

FEEDBACK_PATH = "data_storage/feedback.txt"
os.makedirs(os.path.dirname(FEEDBACK_PATH), exist_ok=True)

def save_feedback(chat_id, text):
    with open(FEEDBACK_PATH, "a", encoding="utf-8") as f:
        f.write(f"From {chat_id}: {text}\n{'-'*40}\n")
