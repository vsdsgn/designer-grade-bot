
import os
import json

def save_user_data(chat_id, data):
    try:
        os.makedirs("user_data", exist_ok=True)
        filepath = f"user_data/{chat_id}.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"❌ Ошибка при сохранении user_data для {chat_id}:", e)

def save_json(filepath: str, data: dict):
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"❌ Ошибка при сохранении JSON в {filepath}:", e)
