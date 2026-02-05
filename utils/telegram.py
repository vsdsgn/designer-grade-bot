import logging
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger("designer_grade_bot.telegram")


async def send_message(token: str, chat_id: int, text: str, reply_markup: Optional[Dict[str, Any]] = None) -> bool:
    if not token or chat_id is None:
        logger.error("Missing Telegram token or chat_id")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload: Dict[str, Any] = {"chat_id": chat_id, "text": text}
    if reply_markup:
        payload["reply_markup"] = reply_markup

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
        return True
    except Exception:
        logger.exception("Failed to send message")
        return False


async def send_document(
    token: str,
    chat_id: int,
    file_path: str,
    caption: Optional[str] = None,
) -> bool:
    if not token or chat_id is None:
        logger.error("Missing Telegram token or chat_id")
        return False

    url = f"https://api.telegram.org/bot{token}/sendDocument"

    try:
        with open(file_path, "rb") as file_handle:
            files = {"document": (file_path.split("/")[-1], file_handle, "application/pdf")}
            data: Dict[str, Any] = {"chat_id": chat_id}
            if caption:
                data["caption"] = caption

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, data=data, files=files)
                response.raise_for_status()
        return True
    except Exception:
        logger.exception("Failed to send document")
        return False


async def set_webhook(token: str, url: str, secret_token: str = "") -> bool:
    if not token or not url:
        logger.error("Missing Telegram token or webhook url")
        return False

    endpoint = f"https://api.telegram.org/bot{token}/setWebhook"
    payload: Dict[str, Any] = {"url": url}
    if secret_token:
        payload["secret_token"] = secret_token

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(endpoint, json=payload)
            response.raise_for_status()
        return True
    except Exception:
        logger.exception("Failed to set webhook")
        return False
