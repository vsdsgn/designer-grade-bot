import json
import logging
import os
from typing import List

from utils.paths import data_path

logger = logging.getLogger("designer_grade_bot.matrices")


def load_competency_context() -> str:
    """
    Loads all files from data/matrices and concatenates them into a short context
    string for the model. Supports JSON or plain text.
    """
    folder = data_path("matrices")
    if not os.path.exists(folder):
        logger.info("No matrices folder found; using default rubric")
        return ""

    chunks: List[str] = []
    for name in sorted(os.listdir(folder)):
        path = os.path.join(folder, name)
        if not os.path.isfile(path):
            continue
        try:
            with open(path, "r", encoding="utf-8") as file:
                raw = file.read().strip()
            if not raw:
                continue
            try:
                data = json.loads(raw)
                pretty = json.dumps(data, ensure_ascii=False, indent=2)
                chunks.append(f"--- {name} ---\n{pretty}")
            except json.JSONDecodeError:
                chunks.append(f"--- {name} ---\n{raw}")
        except Exception:
            logger.exception("Failed to load matrix %s", name)

    # cap context length
    context = "\n\n".join(chunks)
    if len(context) > 8000:
        context = context[:8000] + "\n[truncated]"
    return context
