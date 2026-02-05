import asyncio
import json
import logging
import os
import re
from typing import Any, Dict, List, Optional

from openai import OpenAI

logger = logging.getLogger("designer_grade_bot.grade")

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1")

SYSTEM_PROMPT = (
    "Ты лид-дизайнер. На основе истории интервью определи грейд дизайнера. "
    "Верни JSON с полями: grade, summary, recommendations (list), materials (list). "
    "materials: список объектов с title и url. "
    "Пиши кратко и по делу. Язык ответа: {language}."
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def _format_history(history: List[Dict[str, str]]) -> str:
    lines = []
    for item in history:
        role = item.get("role", "")
        content = item.get("content", "")
        if not content:
            continue
        prefix = "User" if role == "user" else "Assistant"
        lines.append(f"{prefix}: {content}")
    return "\n".join(lines)


def _extract_json(text: str) -> Optional[Dict[str, Any]]:
    text = text.strip()
    if text.startswith("{") and text.endswith("}"):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return None

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


def _normalize_report(data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "grade": str(data.get("grade") or "").strip() or "Unknown",
        "summary": str(data.get("summary") or "").strip(),
        "recommendations": list(data.get("recommendations") or []),
        "materials": list(data.get("materials") or []),
    }


async def grade_user_from_history(
    history: List[Dict[str, str]], language: str = "ru"
) -> Optional[Dict[str, Any]]:
    prompt = SYSTEM_PROMPT.format(language=language)
    transcript = _format_history(history)
    if transcript:
        prompt = f"{prompt}\n\nИстория:\n{transcript}"

    def _call_openai() -> str:
        response = client.responses.create(
            model=OPENAI_MODEL,
            input=prompt,
            temperature=0.4,
        )
        return response.output_text

    try:
        # OpenAI SDK call is blocking; run it in a worker thread.
        text = await asyncio.to_thread(_call_openai)
    except Exception:
        logger.exception("OpenAI grading failed")
        return None

    if not text:
        return None

    data = _extract_json(text)
    if data is None:
        return {
            "grade": "Unknown",
            "summary": text.strip(),
            "recommendations": [],
            "materials": [],
        }

    return _normalize_report(data)
