
import json
import os

SAVE_DIR = "data_storage"
os.makedirs(SAVE_DIR, exist_ok=True)

def save_json(chat_id, session_data):
    path = os.path.join(SAVE_DIR, f"{chat_id}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(session_data, f, ensure_ascii=False, indent=2)
