import asyncio
import logging
import os
from typing import Dict, List, Optional

from openai import OpenAI

logger = logging.getLogger("designer_grade_bot.feedback_prompt")

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1")

SYSTEM_PROMPT = (
    "Generate a single short feedback question for the user about the experience. "
    "It should be specific and helpful. Output only the question. Language: {language}."
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


async def generate_feedback_question(
    history: List[Dict[str, str]], language: str = "ru"
) -> Optional[str]:
    prompt = SYSTEM_PROMPT.format(language=language)
    transcript = _format_history(history)
    if transcript:
        prompt = f"{prompt}\n\nConversation:\n{transcript}"

    def _call_openai() -> str:
        response = client.responses.create(
            model=OPENAI_MODEL,
            input=prompt,
            temperature=0.5,
        )
        return response.output_text

    try:
        text = await asyncio.to_thread(_call_openai)
    except Exception:
        logger.exception("OpenAI feedback prompt failed")
        return None

    return text.strip() if text else None
