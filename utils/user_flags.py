import asyncio
import json
import logging
import os
from typing import Any, Dict

from utils.paths import data_path

logger = logging.getLogger("designer_grade_bot.flags")


def _load_flags(file_path: str) -> Dict[str, Dict[str, bool]]:
    if not os.path.exists(file_path):
        return {}

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError:
        return {}

    if not isinstance(data, dict):
        return {}

    return data


def _save_flags(file_path: str, flags: Dict[str, Dict[str, bool]]) -> bool:
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(flags, file, ensure_ascii=False, indent=2)
    return True


async def load_user_flags() -> Dict[str, Dict[str, bool]]:
    file_path = data_path("user_flags.json")
    try:
        return await asyncio.to_thread(_load_flags, file_path)
    except Exception:
        logger.exception("Failed to load user flags")
        return {}


async def update_user_flags(user_id: int, paid: bool, free_used: bool) -> bool:
    file_path = data_path("user_flags.json")
    try:
        flags = await asyncio.to_thread(_load_flags, file_path)
        flags[str(user_id)] = {"paid": paid, "free_used": free_used}
        return await asyncio.to_thread(_save_flags, file_path, flags)
    except Exception:
        logger.exception("Failed to update user flags")
        return False
