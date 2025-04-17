import os
import json
from fastapi import FastAPI, Request
from app.utils.telegram import send_message, send_document, delete_inline_keyboard
from app.core.dialog_engine import get_next_question
from app.logic.grade_engine import grade_user_from_history
from app.utils.pdf_report import generate_pdf_report
from app.utils.save_to_json import save_user_data, save_json
from app.utils.feedback import handle_feedback

app = FastAPI()

USER_SESSIONS = {}
PAID_USERS = set()

@app.post("/webhook")
async def telegram_webhook(request: Request):
    try:
        data = await request.json()

        if "message" in data:
            message = data["message"]
            chat_id = str(message["chat"]["id"])
            username = message["from"].get("first_name", "друг")
            text = message.get("text", "").strip()
            user_lang = message["from"].get("language_code", "en")
        elif "callback_query" in data:
            message = data["callback_query"]["message"]
            chat_id = str(message["chat"]["id"])
            message_id = message["message_id"]
            user_lang = data["callback_query"]["from"].get("language_code", "en")
            await delete_inline_keyboard(chat_id, message_id)
            text = "/start"
            username = data["callback_query"]["from"].get("first_name", "друг")
        else:
            return {"ok": True}

        print(f"➡️ Text: {text} | Chat ID: {chat_id} | Lang: {user_lang}")

        if text == "/start":
            USER_SESSIONS[chat_id] = {"messages": [], "lang": user_lang}
            welcome = (
                f"Привет, {username}!"

""
"Этот бот поможет определить твой дизайнерский грейд через диалог."

""
"Формат — как в чате. Отвечай честно и развёрнуто."

""
"В конце ты получишь PDF-отчёт с анализом, рекомендациями и материалами."

""
                "Готов?"
            )
            await send_message(chat_id, welcome)
            next_q = get_next_question(USER_SESSIONS[chat_id])
            await send_message(chat_id, next_q)

        elif text.lower() == "/reset":
            USER_SESSIONS.pop(chat_id, None)
            if chat_id in PAID_USERS:
                await send_message(chat_id, "Грейд сброшен. Для повторного прохождения потребуется оплата.")
            else:
                await send_message(chat_id, "Вы можете пройти тест заново. Отправьте /start.")

        elif text.lower() == "/feedback":
            await send_message(chat_id, "Можешь оставить отзыв о боте или предложить улучшения:")
            USER_SESSIONS[chat_id]["awaiting_feedback"] = True

        elif text.lower() == "/language":
            await send_message(chat_id, "Пожалуйста, напиши на каком языке ты хочешь проходить тест.")
            USER_SESSIONS[chat_id]["awaiting_language"] = True

        elif text.lower() == "/grade":
            history = USER_SESSIONS.get(chat_id, {}).get("messages", [])
            if not history:
                await send_message(chat_id, "Сначала нужно пройти тест.")
            else:
                grade, recommendations, materials = grade_user_from_history(history)
                pdf_path = generate_pdf_report(username, grade, recommendations, materials, history)
                await send_document(chat_id, pdf_path)

        else:
            session = USER_SESSIONS.setdefault(chat_id, {"messages": [], "lang": user_lang})

            if session.get("awaiting_feedback"):
                handle_feedback(chat_id, text)
                session["awaiting_feedback"] = False
                await send_message(chat_id, "Спасибо за отзыв!")
                return {"ok": True}

            if session.get("awaiting_language"):
                session["lang"] = text.lower()
                session["awaiting_language"] = False
                await send_message(chat_id, f"Язык установлен: {text}")
                return {"ok": True}

            session["messages"].append(text)

            if len(session["messages"]) >= 8:
                grade, recommendations, materials = grade_user_from_history(session["messages"])
                pdf_path = generate_pdf_report(username, grade, recommendations, materials, session["messages"])
                await send_document(chat_id, pdf_path)
                await send_message(chat_id, "Если хочешь пройти снова — отправь /reset")
                return {"ok": True}

            next_q = get_next_question(session)
            await send_message(chat_id, next_q)

        return {"ok": True}

    except Exception as e:
        print(f"🔥 Ошибка в webhook: {e}")
        return {"ok": True}