
import os
import json
from fastapi import FastAPI, Request
from app.utils.telegram import send_message, send_document, delete_inline_keyboard
from app.core.dialog_engine import get_next_question
from app.logic.grade_engine import grade_user_from_history
from app.utils.pdf_report import generate_pdf_report
from app.utils.save_to_json import save_user_data
from app.utils.feedback import save_feedback

app = FastAPI()

USER_SESSIONS = {}
PAID_USERS = set()

@app.post("/webhook")
async def telegram_webhook(request: Request):
    try:
        data = await request.json()

        chat_id = None
        text = ""
        username = "друг"
        user_lang = "en"
        message_id = None

        if "message" in data and isinstance(data["message"], dict):
            message = data["message"]
            if not isinstance(message.get("chat"), dict):
                print("⚠️ Unexpected format in message:", data)
                return {"status": "ignored"}

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
            username = data["callback_query"]["from"].get("first_name", "друг")
            text = data["callback_query"]["data"].strip()
        else:
            return {"status": "ignored"}

        # Инициализируем сессию
        session = USER_SESSIONS.setdefault(chat_id, {"messages": [], "lang": user_lang, "paid": False})

        # Команды
        if text == "/start":
            if session.get("paid"):
                await send_message(chat_id, "Вы уже проходили тест. Повторное прохождение будет платным.")
                return

            welcome = f"Привет, {username}! Это тест по грейдам дизайнеров. Первый раз — бесплатно ✅"
            await send_message(chat_id, welcome)
            next_q = get_next_question(session)
            if next_q:
                await send_message(chat_id, next_q)
            else:
                await send_message(chat_id, "Что-то пошло не так. Попробуй позже.")

        elif text == "/reset":
            USER_SESSIONS.pop(chat_id, None)
            await send_message(chat_id, "Грейд сброшен. Для повторного прохождения потребуется оплата.")

        elif text == "/grade":
            await send_message(chat_id, "Вы можете пройти тест заново. Отправьте /start.")

        elif text == "/feedback":
            await send_message(chat_id, "Можешь оставить отзыв о боте или предложить улучшения:")
            session["awaiting_feedback"] = True

        elif text == "/language":
            await send_message(chat_id, "Пожалуйста, напиши, на каком языке ты хочешь пройти тест.")

        elif session.get("awaiting_feedback"):
            session["awaiting_feedback"] = False
            save_feedback(chat_id, text)
            await send_message(chat_id, "Спасибо за фидбек!")

        else:
            session["messages"].append(text)
            next_q = get_next_question(session)
            if next_q:
                await send_message(chat_id, next_q)
            else:
                result = grade_user_from_history(session["messages"])
                session["result"] = result
                session["paid"] = True  # Метим, что тест пройден
                pdf_path = generate_pdf_report(username, result["grade"], result["recommendations"], result["materials"])
                await send_document(chat_id, pdf_path)

        return {"status": "ok"}

    except Exception as e:
        print("🔥 Ошибка в webhook:", e)
        return {"status": "error"}
