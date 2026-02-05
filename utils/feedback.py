import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Any, Dict

from utils.paths import data_path


logger = logging.getLogger("designer_grade_bot.feedback")


def _append_feedback(file_path: str, payload: Dict[str, Any]) -> bool:
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError:
            data = []
    else:
        data = []

    if not isinstance(data, list):
        data = []

    data.append(payload)

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

    return True


async def save_feedback(user_id: int, username: str, text: str) -> bool:
    payload = {
        "user_id": user_id,
        "username": username,
        "text": text,
        "created_at": datetime.utcnow().isoformat(),
    }
    file_path = data_path("feedback.json")
    try:
        return await asyncio.to_thread(_append_feedback, file_path, payload)
    except Exception:
        logger.exception("Failed to save feedback")
        return False
