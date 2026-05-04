import json
from datetime import datetime
import os

DATA_FILE = "data/results.json"

def save_result_to_json(username, language, answers, grade):
    os.makedirs("data", exist_ok=True)
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "username": username,
        "language": language,
        "answers": answers,
        "grade": grade
    }

    data = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []

    data.append(entry)

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
