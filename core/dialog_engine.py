import asyncio
import json
import logging
import os
import re
from typing import Any, Dict, List, Optional

from openai import OpenAI

logger = logging.getLogger("designer_grade_bot.dialog")

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1")

SYSTEM_PROMPT = (
    "Ты проводишь интервью, чтобы определить грейд дизайнера. "
    "Задавай один вопрос за раз, опираясь на историю. "
    "Когда информации достаточно, верни JSON с done=true и пустым next_question. "
    "Иначе верни JSON с done=false и вопросом. "
    "Язык вопроса: {language}."
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

    # Try to find a JSON object inside the text
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


async def generate_next_question(
    history: List[Dict[str, str]], language: str = "ru"
) -> Optional[str]:
    """
    Returns:
        - next question as non-empty string
        - "" when dialog is complete
        - None on error
    """
    prompt = SYSTEM_PROMPT.format(language=language)
    transcript = _format_history(history)
    if transcript:
        prompt = f"{prompt}\n\nИстория:\n{transcript}"

    def _call_openai() -> str:
        response = client.responses.create(
            model=OPENAI_MODEL,
            input=prompt,
            temperature=0.6,
        )
        return response.output_text

    try:
        # OpenAI SDK call is blocking; run it in a worker thread.
        text = await asyncio.to_thread(_call_openai)
    except Exception:
        logger.exception("OpenAI dialog generation failed")
        return None

    if not text:
        return ""

    data = _extract_json(text)
    if data is not None:
        next_question = str(data.get("next_question") or "").strip()
        done = bool(data.get("done"))
        if done or not next_question:
            return ""
        return next_question

    # Fallback: model returned plain text
    cleaned = text.strip()
    if cleaned.lower() in {"done", "stop", "end"}:
        return ""

    return cleaned
