import os
import json
from fastapi import FastAPI, Request
from app.utils.telegram import send_message, send_document, delete_inline_keyboard
from app.core.dialog_engine import get_next_question
from app.logic.grade_engine import grade_user_from_history
from app.utils.pdf_report import generate_pdf_report
from app.utils.save_to_json import save_user_data, save_json
from app.utils.feedback import save_feedback

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
                f"""Привет, {username}!

                Этот бот поможет определить твой дизайнерский грейд через диалог.

                Формат — как в чате. Отвечай честно и развёрнуто.

                В конце ты получишь PDF-отчёт с анализом, рекомендациями и материалами.

                Готов?"""
            )
            await send_message(chat_id, welcome, )

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
            await send_message(chat_id, f"""Пожалуйста, напиши на каком языке ты хочешь проходить тест.

Например: English, Русский, Español, 中文...""")
            USER_SESSIONS[chat_id]["awaiting_language"] = True

        elif text.lower() == "/grade":
            history = USER_SESSIONS.get(chat_id, {}).get("messages", [])
            if not history:
                await send_message(chat_id, "Сначала нужно пройти тест.")
            else:
                result = await grade_user_from_history(history)
                pdf_path = generate_pdf_report(result, username)
                await send_document(chat_id, pdf_path)

        elif chat_id in USER_SESSIONS:
            session = USER_SESSIONS[chat_id]
            if session.get("awaiting_feedback"):
                save_feedback(chat_id, text)
                await send_message(chat_id, "Спасибо за отзыв!")
                session["awaiting_feedback"] = False
            elif session.get("awaiting_language"):
                session["lang"] = text.lower()
                await send_message(chat_id, f"Язык установлен: {text}")
                session["awaiting_language"] = False
            else:
                messages = session.setdefault("messages", [])
                messages.append({"role": "user", "content": text})
                save_json(chat_id, messages)
                reply = await get_next_question(chat_id, text, session["lang"])
                if reply:
                    await send_message(chat_id, reply)
                else:
                    await send_message(chat_id, "Спасибо! Формирую результаты...")
                    result = await grade_user_from_history(messages)
                    pdf_path = generate_pdf_report(result, username)
                    await send_document(chat_id, pdf_path)
                    PAID_USERS.add(chat_id)
        else:
            await send_message(chat_id, "Пожалуйста, начни с команды /start")

        return {"ok": True}

    except Exception as e:
        print("🔥 Ошибка в webhook:", str(e))
        return {"ok": False, "error": str(e)}