import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional

import asyncpg

from utils.paths import data_path

logger = logging.getLogger("designer_grade_bot.db")

DATABASE_URL = os.getenv("DATABASE_URL", "")


async def init_db() -> Optional[asyncpg.Pool]:
    if not DATABASE_URL:
        logger.info(
            "DATABASE_URL not set; using file storage under DATA_DIR=%s",
            os.getenv("DATA_DIR", "data"),
        )
        return None

    try:
        return await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5)
    except Exception:
        logger.exception("Failed to init database pool")
        return None


async def ensure_schema(pool: Optional[asyncpg.Pool]) -> None:
    if pool is None:
        return

    try:
        async with pool.acquire() as conn:
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS feedback (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT,
                    username TEXT,
                    language TEXT,
                    question TEXT,
                    answer TEXT,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );

                CREATE TABLE IF NOT EXISTS user_state (
                    user_id BIGINT PRIMARY KEY,
                    free_used BOOLEAN DEFAULT FALSE,
                    paid BOOLEAN DEFAULT FALSE,
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                );
                """
            )
    except Exception:
        logger.exception("Failed to ensure schema")


def _load_json_map(file_path: str) -> Dict[str, Dict[str, Any]]:
    if not os.path.exists(file_path):
        return {}

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError:
        return {}

    return data if isinstance(data, dict) else {}


def _save_json_map(file_path: str, data: Dict[str, Dict[str, Any]]) -> None:
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def _load_json_list(file_path: str) -> list:
    if not os.path.exists(file_path):
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError:
        return []

    return data if isinstance(data, list) else []


def _save_json_list(file_path: str, data: list) -> None:
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


async def get_user_state(pool: Optional[asyncpg.Pool], user_id: int) -> Dict[str, bool]:
    if pool is None:
        file_path = data_path("user_state.json")
        try:
            data = await asyncio.to_thread(_load_json_map, file_path)
            record = data.get(str(user_id), {})
            return {
                "free_used": bool(record.get("free_used", False)),
                "paid": bool(record.get("paid", False)),
            }
        except Exception:
            logger.exception("Failed to load local user state")
            return {"free_used": False, "paid": False}

    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT free_used, paid FROM user_state WHERE user_id = $1",
                user_id,
            )
            if not row:
                return {"free_used": False, "paid": False}
            return {"free_used": bool(row["free_used"]), "paid": bool(row["paid"])}
    except Exception:
        logger.exception("Failed to fetch user state")
        return {"free_used": False, "paid": False}


async def upsert_user_state(
    pool: Optional[asyncpg.Pool], user_id: int, paid: bool, free_used: bool
) -> None:
    if pool is None:
        file_path = data_path("user_state.json")
        try:
            data = await asyncio.to_thread(_load_json_map, file_path)
            data[str(user_id)] = {
                "paid": bool(paid),
                "free_used": bool(free_used),
                "updated_at": datetime.utcnow().isoformat(),
            }
            await asyncio.to_thread(_save_json_map, file_path, data)
        except Exception:
            logger.exception("Failed to save local user state")
        return

    try:
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO user_state (user_id, free_used, paid, updated_at)
                VALUES ($1, $2, $3, NOW())
                ON CONFLICT (user_id)
                DO UPDATE SET free_used = $2, paid = $3, updated_at = NOW()
                """,
                user_id,
                free_used,
                paid,
            )
    except Exception:
        logger.exception("Failed to upsert user state")


async def save_feedback(
    pool: Optional[asyncpg.Pool],
    user_id: int,
    username: str,
    language: str,
    question: Optional[str],
    answer: str,
) -> bool:
    if pool is None:
        file_path = data_path("feedback.json")
        payload = {
            "user_id": user_id,
            "username": username,
            "language": language,
            "question": question,
            "answer": answer,
            "created_at": datetime.utcnow().isoformat(),
        }
        try:
            data = await asyncio.to_thread(_load_json_list, file_path)
            data.append(payload)
            await asyncio.to_thread(_save_json_list, file_path, data)
            return True
        except Exception:
            logger.exception("Failed to save feedback locally")
            return False

    try:
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO feedback (user_id, username, language, question, answer)
                VALUES ($1, $2, $3, $4, $5)
                """,
                user_id,
                username,
                language,
                question,
                answer,
            )
        return True
    except Exception:
        logger.exception("Failed to save feedback")
        return False
