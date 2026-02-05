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
    "You are a senior product design consultant. "
    "Your goal is to gather enough information to assess a designer's grade. "
    "Ask one open question at a time and adapt to answers. "
    "If you have enough information, return JSON: {\"done\": true, \"next_question\": \"\"}. "
    "Otherwise return JSON: {\"done\": false, \"next_question\": \"...\"}. "
    "Language: {language}."
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


async def generate_next_question(
    history: List[Dict[str, str]], matrix_context: str, language: str = "ru"
) -> Optional[str]:
    prompt = SYSTEM_PROMPT.format(language=language)
    transcript = _format_history(history)
    if matrix_context:
        prompt = f"{prompt}\n\nCompetency matrices:\n{matrix_context}"
    if transcript:
        prompt = f"{prompt}\n\nConversation:\n{transcript}"

    def _call_openai() -> str:
        response = client.responses.create(
            model=OPENAI_MODEL,
            input=prompt,
            temperature=0.6,
        )
        return response.output_text

    try:
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

    cleaned = text.strip()
    if cleaned.lower() in {"done", "stop", "end"}:
        return ""

    return cleaned
