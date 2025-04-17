import json
from pathlib import Path

def save_user_data(chat_id: str, data: dict):
    Path("user_data").mkdir(parents=True, exist_ok=True)
    filepath = f"user_data/{chat_id}.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def save_json(filepath: str, data: dict):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)