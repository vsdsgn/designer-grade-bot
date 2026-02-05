import asyncio
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from core.dialog_engine import generate_next_question
from core.feedback_engine import generate_feedback_question
from logic.grade_engine import grade_user_from_history
from utils.db import (
    init_db,
    ensure_schema,
    get_user_state,
    save_feedback,
    upsert_user_state,
)
from utils.matrices import load_competency_context
from utils.pdf_report import generate_pdf_report
from utils.telegram import send_document, send_message, set_webhook
from utils.paths import data_path

app = FastAPI(title="Designer Grade Bot")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("designer_grade_bot")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_WEBHOOK_SECRET = os.getenv("TELEGRAM_WEBHOOK_SECRET", "")
PUBLIC_URL = os.getenv("PUBLIC_URL", "")
AUTO_SET_WEBHOOK = os.getenv("AUTO_SET_WEBHOOK", "false").lower() == "true"

# In-memory session store
USER_SESSIONS: Dict[int, Dict[str, Any]] = {}
COMPETENCY_CONTEXT: str = ""
DB_POOL = None


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/webhook")
async def telegram_webhook(request: Request) -> JSONResponse:
    try:
        if TELEGRAM_WEBHOOK_SECRET:
            secret_header = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
            if secret_header != TELEGRAM_WEBHOOK_SECRET:
                logger.warning("Invalid Telegram webhook secret")
                return JSONResponse({"ok": False}, status_code=403)

        update = await request.json()
        logger.info("Incoming webhook update_id=%s", update.get("update_id"))
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


def _user_display_name(user: Dict[str, Any]) -> str:
    username = user.get("username")
    if username:
        return f"@{username}"
    first_name = user.get("first_name", "")
    last_name = user.get("last_name", "")
    full_name = (first_name + " " + last_name).strip()
    return full_name or "Unknown"


def _retake_text(language: str) -> str:
    return "Пройти заново" if language == "ru" else "Retake"


def _language_prompt(language: str) -> str:
    return "Выберите язык: ru или en" if language == "ru" else "Choose language: ru or en"


def _feedback_thanks(language: str) -> str:
    return "Спасибо за отзыв!" if language == "ru" else "Thanks for the feedback!"


def _free_locked_message(language: str) -> str:
    if language == "ru":
        return "Первое прохождение уже использовано. Для повторного требуется оплата."
    return "Your free attempt is used. Payment is required for another run."


def _pdf_locked_message(language: str) -> str:
    if language == "ru":
        return "Полный PDF-отчёт доступен после оплаты."
    return "The full PDF report is available after payment."


def _summary_header(language: str) -> str:
    return "Краткое резюме" if language == "ru" else "Summary"


def _grade_label(language: str) -> str:
    return "Грейд" if language == "ru" else "Grade"


def _strengths_label(language: str) -> str:
    return "Сильные стороны" if language == "ru" else "Strengths"


def _weaknesses_label(language: str) -> str:
    return "Зоны роста" if language == "ru" else "Growth areas"


async def handle_update(update: Dict[str, Any]) -> None:
    message = update.get("message") or update.get("edited_message")
    if not message:
        logger.info("Update without message payload was ignored")
        return

    user = message.get("from", {})
    user_id = user.get("id")
    if user_id is None:
        logger.info("Message without user_id was ignored")
        return

    chat = message.get("chat", {})
    chat_id = chat.get("id")
    if chat_id is None:
        logger.info("Message without chat_id was ignored")
        return

    text = message.get("text")
    if text is None:
        logger.info("Non-text message was ignored")
        return

    logger.info("Message received chat_id=%s user_id=%s text=%s", chat_id, user_id, text)

    session = await _get_or_create_session(user_id, user)

    # handle retake button
    if text.strip().lower() in {"пройти заново", "retake"}:
        text = "/start"

    # language selection flow
    if session.get("awaiting_language") and not text.startswith("/"):
        await _handle_language_selection(session, chat_id, text)
        return

    # feedback flow
    if session.get("awaiting_feedback") and not text.startswith("/"):
        await _handle_feedback(session, chat_id, user_id, text)
        return

    if text.startswith("/"):
        await _handle_command(session, chat_id, user_id, text)
        return

    if session.get("state") == "collecting":
        await _handle_dialog_message(session, chat_id, user_id, text)
        return

    await send_message(
        TELEGRAM_BOT_TOKEN,
        chat_id,
        "Напишите /start, чтобы начать тест." if session["language"] == "ru" else "Send /start to begin.",
    )


async def _get_or_create_session(user_id: int, user: Dict[str, Any]) -> Dict[str, Any]:
    session = USER_SESSIONS.get(user_id)
    if session is None:
        flags = await get_user_state(DB_POOL, user_id)
        session = {
            "history": [],
            "language": "ru",
            "paid": bool(flags.get("paid", False)),
            "free_used": bool(flags.get("free_used", False)),
            "state": "idle",
            "awaiting_language": False,
            "awaiting_feedback": False,
            "username": _user_display_name(user),
            "last_report": None,
        }
        USER_SESSIONS[user_id] = session
    else:
        session["username"] = _user_display_name(user)
    return session


async def _handle_command(session: Dict[str, Any], chat_id: int, user_id: int, text: str) -> None:
    command = text.split()[0].lower()

    if command == "/start":
        await _start_dialog(session, chat_id, user_id)
        return

    if command == "/reset":
        session["history"] = []
        session["state"] = "idle"
        session["awaiting_language"] = False
        session["awaiting_feedback"] = False
        await send_message(TELEGRAM_BOT_TOKEN, chat_id, "Прогресс сброшен." if session["language"] == "ru" else "Progress reset.")
        return

    if command == "/language":
        session["awaiting_language"] = True
        await send_message(TELEGRAM_BOT_TOKEN, chat_id, _language_prompt(session["language"]))
        return

    if command == "/feedback":
        session["awaiting_feedback"] = True
        question = await generate_feedback_question(session["history"], session["language"])
        if not question:
            question = "Что можно улучшить?" if session["language"] == "ru" else "What could be improved?"
        session["last_feedback_question"] = question
        await send_message(TELEGRAM_BOT_TOKEN, chat_id, question)
        return

    if command == "/pay":
        # payment hook placeholder
        session["paid"] = True
        await upsert_user_state(DB_POOL, user_id, paid=True, free_used=session.get("free_used", False))
        await send_message(
            TELEGRAM_BOT_TOKEN,
            chat_id,
            "Оплата подтверждена (эмуляция)." if session["language"] == "ru" else "Payment confirmed (simulated).",
        )
        # If a report exists, deliver PDF now
        if session.get("last_report"):
            await _send_pdf_report(session, chat_id, user_id)
        return

    await send_message(TELEGRAM_BOT_TOKEN, chat_id, "Неизвестная команда." if session["language"] == "ru" else "Unknown command.")


async def _start_dialog(session: Dict[str, Any], chat_id: int, user_id: int) -> None:
    if session.get("free_used") and not session.get("paid"):
        await send_message(TELEGRAM_BOT_TOKEN, chat_id, _free_locked_message(session["language"]))
        return

    session["history"] = []
    session["state"] = "collecting"
    session["awaiting_language"] = False
    session["awaiting_feedback"] = False
    session["last_report"] = None

    intro = (
        "Начинаем интервью. Отвечайте развернуто." if session["language"] == "ru" else "Starting interview. Please answer in detail."
    )
    await send_message(TELEGRAM_BOT_TOKEN, chat_id, intro)

    next_question = await generate_next_question(session["history"], COMPETENCY_CONTEXT, session["language"])
    if next_question is None:
        await send_message(TELEGRAM_BOT_TOKEN, chat_id, "Не удалось сгенерировать вопрос." if session["language"] == "ru" else "Failed to generate a question.")
        session["state"] = "idle"
        return

    if next_question:
        session["history"].append({"role": "assistant", "content": next_question})
        await send_message(TELEGRAM_BOT_TOKEN, chat_id, next_question)
        return

    await _finalize_grade(session, chat_id, user_id)


async def _handle_dialog_message(session: Dict[str, Any], chat_id: int, user_id: int, text: str) -> None:
    session["history"].append({"role": "user", "content": text})

    next_question = await generate_next_question(session["history"], COMPETENCY_CONTEXT, session["language"])
    if next_question is None:
        await send_message(TELEGRAM_BOT_TOKEN, chat_id, "Не удалось продолжить." if session["language"] == "ru" else "Failed to continue.")
        return

    if next_question:
        session["history"].append({"role": "assistant", "content": next_question})
        await send_message(TELEGRAM_BOT_TOKEN, chat_id, next_question)
        return

    await _finalize_grade(session, chat_id, user_id)


async def _finalize_grade(session: Dict[str, Any], chat_id: int, user_id: int) -> None:
    report = await grade_user_from_history(session["history"], COMPETENCY_CONTEXT, session["language"])
    if report is None:
        await send_message(TELEGRAM_BOT_TOKEN, chat_id, "Не удалось определить грейд." if session["language"] == "ru" else "Failed to determine grade.")
        session["state"] = "idle"
        return

    session["last_report"] = report

    summary_text = _format_summary(report, session["language"])
    await send_message(TELEGRAM_BOT_TOKEN, chat_id, summary_text)

    if session.get("paid"):
        await _send_pdf_report(session, chat_id, user_id)
    else:
        await send_message(TELEGRAM_BOT_TOKEN, chat_id, _pdf_locked_message(session["language"]))

    session["free_used"] = True
    session["state"] = "completed"
    await upsert_user_state(DB_POOL, user_id, paid=session.get("paid", False), free_used=True)

    await _send_retake_button(session, chat_id)


async def _send_pdf_report(session: Dict[str, Any], chat_id: int, user_id: int) -> None:
    report = session.get("last_report")
    if not report:
        return

    user_display_name = session.get("username", "Unknown")
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    file_path = data_path("reports", f"report_{chat_id}_{timestamp}.pdf")

    pdf_path = await generate_pdf_report(report, user_display_name, file_path)
    if not pdf_path:
        await send_message(TELEGRAM_BOT_TOKEN, chat_id, "Не удалось сформировать PDF." if session["language"] == "ru" else "Failed to generate PDF.")
        return

    await send_document(
        TELEGRAM_BOT_TOKEN,
        chat_id,
        pdf_path,
        caption="Ваш PDF-отчёт" if session["language"] == "ru" else "Your PDF report",
    )


async def _handle_language_selection(session: Dict[str, Any], chat_id: int, text: str) -> None:
    language = text.strip().lower()
    if language in {"русский", "ru"}:
        language = "ru"
    elif language in {"english", "en"}:
        language = "en"

    if language not in {"ru", "en"}:
        await send_message(TELEGRAM_BOT_TOKEN, chat_id, "Поддерживаются только ru или en." if session["language"] == "ru" else "Only ru or en supported.")
        return

    session["language"] = language
    session["awaiting_language"] = False
    await send_message(TELEGRAM_BOT_TOKEN, chat_id, f"Язык установлен: {language}." if language == "ru" else f"Language set: {language}.")


async def _handle_feedback(session: Dict[str, Any], chat_id: int, user_id: int, text: str) -> None:
    session["awaiting_feedback"] = False
    question = session.get("last_feedback_question")
    saved = await save_feedback(
        DB_POOL,
        user_id=user_id,
        username=session.get("username", "Unknown"),
        language=session.get("language", "ru"),
        question=question,
        answer=text,
    )
    if saved:
        await send_message(TELEGRAM_BOT_TOKEN, chat_id, _feedback_thanks(session["language"]))
        return

    await send_message(TELEGRAM_BOT_TOKEN, chat_id, "Не удалось сохранить отзыв." if session["language"] == "ru" else "Failed to save feedback.")


async def _send_retake_button(session: Dict[str, Any], chat_id: int) -> None:
    button_text = _retake_text(session["language"])
    reply_markup = {
        "keyboard": [[{"text": button_text}]],
        "resize_keyboard": True,
        "one_time_keyboard": True,
    }
    await send_message(
        TELEGRAM_BOT_TOKEN,
        chat_id,
        "Готовы пройти заново?" if session["language"] == "ru" else "Ready to retake?",
        reply_markup=reply_markup,
    )


def _format_summary(report: Dict[str, Any], language: str) -> str:
    grade = report.get("grade", "Unknown")
    summary = report.get("summary", "")
    strengths = report.get("strengths", [])
    weaknesses = report.get("weaknesses", [])

    lines: List[str] = []
    lines.append(f"{_summary_header(language)}")
    lines.append(f"{_grade_label(language)}: {grade}")
    if summary:
        lines.append(summary)
    if strengths:
        lines.append(f"{_strengths_label(language)}: " + ", ".join(strengths))
    if weaknesses:
        lines.append(f"{_weaknesses_label(language)}: " + ", ".join(weaknesses))

    return "\n".join(lines)


@app.on_event("startup")
async def on_startup() -> None:
    global COMPETENCY_CONTEXT, DB_POOL

    COMPETENCY_CONTEXT = load_competency_context()
    DB_POOL = await init_db()
    await ensure_schema(DB_POOL)

    if not TELEGRAM_BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN is not set")
    if not os.getenv("OPENAI_API_KEY"):
        logger.warning("OPENAI_API_KEY is not set")

    if AUTO_SET_WEBHOOK and TELEGRAM_BOT_TOKEN and PUBLIC_URL:
        webhook_url = f"{PUBLIC_URL.rstrip('/')}/webhook"
        webhook_ok = await set_webhook(
            TELEGRAM_BOT_TOKEN,
            webhook_url,
            TELEGRAM_WEBHOOK_SECRET,
        )
        logger.info("Webhook registration result=%s url=%s", webhook_ok, webhook_url)
