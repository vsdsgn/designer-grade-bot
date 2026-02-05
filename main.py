import asyncio
import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from core.dialog_engine import generate_next_question
from logic.grade_engine import grade_user_from_history
from utils.pdf_report import generate_pdf_report
from utils.paths import data_path
from utils.save_to_json import save_user_result
from utils.telegram import send_document, send_message
from utils.telegram import set_webhook
from utils.feedback import save_feedback
from utils.user_flags import load_user_flags, update_user_flags

app = FastAPI(title="Designer Grade Bot")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("designer_grade_bot")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_WEBHOOK_SECRET = os.getenv("TELEGRAM_WEBHOOK_SECRET", "")
PUBLIC_URL = os.getenv("PUBLIC_URL", "")

# In-memory session store
USER_SESSIONS: Dict[int, Dict[str, Any]] = {}
USER_FLAGS: Dict[str, Dict[str, bool]] = {}


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/webhook")
async def telegram_webhook(request: Request) -> JSONResponse:
    """Telegram webhook endpoint."""
    try:
        if TELEGRAM_WEBHOOK_SECRET:
            secret_header = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
            if secret_header != TELEGRAM_WEBHOOK_SECRET:
                logger.warning("Invalid Telegram webhook secret")
                return JSONResponse({"ok": False}, status_code=403)

        update = await request.json()
        # Process in background to respond quickly to Telegram
        asyncio.create_task(_safe_handle_update(update))
        return JSONResponse({"ok": True})
    except Exception:
        logger.exception("Webhook error")
        return JSONResponse({"ok": False}, status_code=500)


async def _safe_handle_update(update: Dict[str, Any]) -> None:
    try:
        await handle_update(update)
    except Exception:
        logger.exception("Update handling failed")


def _get_session(user_id: int, user: Dict[str, Any]) -> Dict[str, Any]:
    session = USER_SESSIONS.get(user_id)
    flags = USER_FLAGS.get(str(user_id), {})
    if session is None:
        session = {
            "history": [],
            "language": "ru",
            "paid": bool(flags.get("paid", False)),
            "free_used": bool(flags.get("free_used", False)),
            "state": "idle",
            "awaiting_language": False,
            "awaiting_feedback": False,
            "username": _user_display_name(user),
        }
        USER_SESSIONS[user_id] = session
    else:
        # Keep username fresh
        session["username"] = _user_display_name(user)
        # Sync flags if they were updated on disk
        session["paid"] = bool(flags.get("paid", session.get("paid", False)))
        session["free_used"] = bool(flags.get("free_used", session.get("free_used", False)))
    return session


def _user_display_name(user: Dict[str, Any]) -> str:
    username = user.get("username")
    if username:
        return f"@{username}"
    first_name = user.get("first_name", "")
    last_name = user.get("last_name", "")
    full_name = (first_name + " " + last_name).strip()
    return full_name or "Unknown"


async def handle_update(update: Dict[str, Any]) -> None:
    message = update.get("message") or update.get("edited_message")
    if not message:
        return

    user = message.get("from", {})
    user_id = user.get("id")
    if user_id is None:
        return

    chat = message.get("chat", {})
    chat_id = chat.get("id")
    if chat_id is None:
        return

    text = message.get("text")
    if text is None:
        return

    session = _get_session(user_id, user)

    # Language selection flow
    if session.get("awaiting_language") and not text.startswith("/"):
        await _handle_language_selection(session, chat_id, text)
        return

    # Feedback flow
    if session.get("awaiting_feedback") and not text.startswith("/"):
        await _handle_feedback(session, chat_id, user_id, text)
        return

    if text.startswith("/"):
        await _handle_command(session, chat_id, user_id, text)
        return

    if session.get("state") == "grading":
        await _handle_dialog_message(session, chat_id, user_id, text)
        return

    await send_message(
        TELEGRAM_BOT_TOKEN,
        chat_id,
        "Напишите /start, чтобы начать оценку грейда дизайнера.",
    )


async def _handle_command(
    session: Dict[str, Any], chat_id: int, user_id: int, text: str
) -> None:
    command = text.split()[0].lower()

    if command == "/start":
        await _start_dialog(session, chat_id, user_id)
        return

    if command == "/reset":
        session["history"] = []
        session["state"] = "idle"
        session["awaiting_language"] = False
        session["awaiting_feedback"] = False
        await send_message(TELEGRAM_BOT_TOKEN, chat_id, "Прогресс сброшен.")
        return

    if command == "/grade":
        await send_message(
            TELEGRAM_BOT_TOKEN,
            chat_id,
            (
                "Повторное прохождение доступно после оплаты. "
                "Для эмуляции используйте /pay."
            ),
        )
        return

    if command == "/language":
        session["awaiting_language"] = True
        await send_message(
            TELEGRAM_BOT_TOKEN,
            chat_id,
            "Выберите язык: ru или en",
        )
        return

    if command == "/feedback":
        session["awaiting_feedback"] = True
        await send_message(
            TELEGRAM_BOT_TOKEN,
            chat_id,
            "Оставьте отзыв одним сообщением.",
        )
        return

    if command == "/pay":
        if not session.get("free_used"):
            await send_message(
                TELEGRAM_BOT_TOKEN,
                chat_id,
                "Оплата пока не требуется. Первое прохождение бесплатное.",
            )
            return

        session["paid"] = True
        await update_user_flags(user_id=user_id, paid=True, free_used=True)
        await send_message(
            TELEGRAM_BOT_TOKEN,
            chat_id,
            "Оплата подтверждена (эмуляция). Теперь можно пройти заново: /start.",
        )
        return

    await send_message(TELEGRAM_BOT_TOKEN, chat_id, "Неизвестная команда.")


async def _start_dialog(session: Dict[str, Any], chat_id: int, user_id: int) -> None:
    if session.get("free_used") and not session.get("paid"):
        await send_message(
            TELEGRAM_BOT_TOKEN,
            chat_id,
            (
                "Первое прохождение уже использовано. "
                "Повторно можно пройти после оплаты. /grade"
            ),
        )
        return

    session["history"] = []
    session["state"] = "grading"
    session["awaiting_language"] = False
    session["awaiting_feedback"] = False

    await send_message(
        TELEGRAM_BOT_TOKEN,
        chat_id,
        "Designer Grade Bot начал интервью. Отвечайте развернуто.",
    )

    next_question = await generate_next_question(session["history"], session["language"])
    if next_question is None:
        await send_message(
            TELEGRAM_BOT_TOKEN,
            chat_id,
            "Не удалось сгенерировать вопрос. Попробуйте /start позже.",
        )
        session["state"] = "idle"
        return

    if next_question:
        session["history"].append({"role": "assistant", "content": next_question})
        await send_message(TELEGRAM_BOT_TOKEN, chat_id, next_question)
        return

    await _finalize_grade(session, chat_id, user_id=user_id)


async def _handle_dialog_message(
    session: Dict[str, Any], chat_id: int, user_id: int, text: str
) -> None:
    session["history"].append({"role": "user", "content": text})

    next_question = await generate_next_question(session["history"], session["language"])
    if next_question is None:
        await send_message(
            TELEGRAM_BOT_TOKEN,
            chat_id,
            "Не удалось продолжить диалог. Попробуйте /reset и /start.",
        )
        return

    if next_question:
        session["history"].append({"role": "assistant", "content": next_question})
        await send_message(TELEGRAM_BOT_TOKEN, chat_id, next_question)
        return

    await _finalize_grade(session, chat_id, user_id)


async def _finalize_grade(
    session: Dict[str, Any], chat_id: int, user_id: Optional[int]
) -> None:
    report = await grade_user_from_history(session["history"], session["language"])
    if report is None:
        await send_message(
            TELEGRAM_BOT_TOKEN,
            chat_id,
            "Не удалось определить грейд. Попробуйте позже.",
        )
        session["state"] = "idle"
        return

    user_display_name = session.get("username", "Unknown")
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    file_path = data_path("reports", f"report_{chat_id}_{timestamp}.pdf")

    pdf_path = await generate_pdf_report(report, user_display_name, file_path)
    if not pdf_path:
        await send_message(
            TELEGRAM_BOT_TOKEN,
            chat_id,
            "Не удалось сформировать PDF-отчёт.",
        )
        session["state"] = "idle"
        return

    await send_document(
        TELEGRAM_BOT_TOKEN,
        chat_id,
        pdf_path,
        caption="Ваш отчёт по грейду дизайнера.",
    )

    # Save data asynchronously
    if user_id is not None:
        await save_user_result(user_id, user_display_name, session["language"], report)

    session["free_used"] = True
    if user_id is not None:
        await update_user_flags(
            user_id=user_id, paid=session.get("paid", False), free_used=True
        )
    session["state"] = "completed"


async def _handle_language_selection(
    session: Dict[str, Any], chat_id: int, text: str
) -> None:
    language = text.strip().lower()
    if language not in {"ru", "en"}:
        await send_message(
            TELEGRAM_BOT_TOKEN,
            chat_id,
            "Поддерживаются только ru или en. Повторите выбор.",
        )
        return

    session["language"] = language
    session["awaiting_language"] = False
    await send_message(
        TELEGRAM_BOT_TOKEN,
        chat_id,
        f"Язык установлен: {language}.",
    )


async def _handle_feedback(
    session: Dict[str, Any], chat_id: int, user_id: int, text: str
) -> None:
    saved = await save_feedback(user_id, session.get("username", "Unknown"), text)
    session["awaiting_feedback"] = False
    if saved:
        await send_message(TELEGRAM_BOT_TOKEN, chat_id, "Спасибо за отзыв!")
        return

    await send_message(
        TELEGRAM_BOT_TOKEN,
        chat_id,
        "Не удалось сохранить отзыв. Попробуйте позже.",
    )


@app.on_event("startup")
async def on_startup() -> None:
    if not TELEGRAM_BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN is not set")

    if not os.getenv("OPENAI_API_KEY"):
        logger.warning("OPENAI_API_KEY is not set")

    global USER_FLAGS
    USER_FLAGS = await load_user_flags()

    if os.getenv("AUTO_SET_WEBHOOK", "false").lower() == "true":
        if TELEGRAM_BOT_TOKEN and PUBLIC_URL:
            await set_webhook(
                TELEGRAM_BOT_TOKEN,
                f"{PUBLIC_URL.rstrip('/')}/webhook",
                TELEGRAM_WEBHOOK_SECRET,
            )
        else:
            logger.warning("AUTO_SET_WEBHOOK is enabled but PUBLIC_URL or TELEGRAM_BOT_TOKEN is missing")
