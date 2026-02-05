import json
import logging
import os
from typing import List

from utils.paths import data_path

logger = logging.getLogger("designer_grade_bot.matrices")


def _matrix_folders() -> List[str]:
    primary = data_path("matrices")
    bundled = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "data", "matrices")
    )
    if primary == bundled:
        return [primary]
    return [primary, bundled]


def load_competency_context() -> str:
    """
    Loads all files from data/matrices and concatenates them into a short context
    string for the model. Supports JSON or plain text.
    """
    chunks: List[str] = []
    used_folder = ""

    for folder in _matrix_folders():
        if not os.path.isdir(folder):
            continue

        local_chunks: List[str] = []
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
                    local_chunks.append(f"--- {name} ---\n{pretty}")
                except json.JSONDecodeError:
                    local_chunks.append(f"--- {name} ---\n{raw}")
            except Exception:
                logger.exception("Failed to load matrix %s", name)

        if local_chunks:
            chunks = local_chunks
            used_folder = folder
            break

    if not chunks:
        logger.info("No matrices found; using default rubric")
        return ""

    logger.info("Loaded %d matrix file(s) from %s", len(chunks), used_folder)

    # cap context length
    context = "\n\n".join(chunks)
    if len(context) > 8000:
        context = context[:8000] + "\n[truncated]"
    return context
