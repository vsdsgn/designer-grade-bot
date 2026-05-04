from fastapi import FastAPI, Request
import os
from dotenv import load_dotenv
from app.utils.telegram import send_message
from app.dialogue.questions import get_questions, get_intro
from app.grading.logic import grade_user
from app.utils.google_sheets import save_result_to_sheet

load_dotenv()
app = FastAPI()
user_states = {}

SUPPORTED_LANGUAGES = {
    "ru": ["ru", "русский", "russian"],
    "en": ["en", "english", "английский"],
}

@app.post("/webhook")
async def telegram_webhook(request: Request):
    body = await request.json()
    message_data = body.get("message") or body.get("callback_query", {}).get("message", {})
    from_data = message_data.get("from", {})
    chat_id = message_data.get("chat", {}).get("id")
    message_text = body.get("message", {}).get("text", "").strip()
    user_lang = from_data.get("language_code", "en")[:2]
    username = from_data.get("username", "unknown")

    language = user_lang if user_lang in SUPPORTED_LANGUAGES else "en"

    if not chat_id or not message_text:
        return {"ok": True}

    if message_text.lower() == "/start":
        user_states[chat_id] = {
            "language": language,
            "step": 0,
            "answers": [],
            "username": username,
            "grade": None
        }
        intro = get_intro(language)
        send_message(chat_id, intro)
        questions = get_questions(language)
        send_message(chat_id, questions[0])
        return {"ok": True}

    if message_text.lower() == "/reset":
        user_states.pop(chat_id, None)
        send_message(chat_id, "🔄 Сессия сброшена. Напиши /start, чтобы пройти тест заново." if language == "ru" else "🔄 Session reset. Type /start to take the test again.")
        return {"ok": True}

    if message_text.lower() == "/grade":
        grade = user_states.get(chat_id, {}).get("grade")
        if grade:
            msg = f"📊 Последний определённый грейд: {grade}" if language == "ru" else f"📊 Last detected grade: {grade}"
        else:
            msg = "❗ Пока нет результатов. Напиши /start, чтобы пройти тест." if language == "ru" else "❗ No results yet. Type /start to take the test."
        send_message(chat_id, msg)
        return {"ok": True}

    if message_text.lower() == "/language":
        msg = "🌍 Напиши язык, на котором хочешь продолжить (например: Русский, English)" if language == "ru" else "🌍 Please type the language you'd like to use (e.g., English, Русский)"
        send_message(chat_id, msg)
        user_states[chat_id] = {"language": None, "step": -1, "answers": [], "username": username}
        return {"ok": True}

    if message_text.lower() == "/feedback":
        msg = "💬 Напиши свой отзыв или пожелание прямо здесь, и я передам его команде. Спасибо! 🙏" if language == "ru" else "💬 You can write your feedback or suggestion here, and I’ll forward it to the team. Thank you! 🙏"
        send_message(chat_id, msg)
        return {"ok": True}

    if chat_id in user_states and user_states[chat_id].get("language") is None:
        selected_lang = message_text.strip().lower()
        for code, aliases in SUPPORTED_LANGUAGES.items():
            if selected_lang in aliases:
                user_states[chat_id]["language"] = code
                user_states[chat_id]["step"] = 0
                intro = get_intro(code)
                send_message(chat_id, intro)
                send_message(chat_id, get_questions(code)[0])
                return {"ok": True}
        send_message(chat_id, "❌ Язык не распознан. Попробуй снова (например: Русский, English)" if language == "ru" else "❌ Language not recognized. Please try again (e.g., English, Русский)")
        return {"ok": True}

    state = user_states.get(chat_id)
    if not state:
        send_message(chat_id, "❗ Пожалуйста, начни с /start." if language == "ru" else "❗ Please start with /start.")
        return {"ok": True}

    step = state["step"]
    language = state["language"]
    state["answers"].append(message_text)
    step += 1

    questions = get_questions(language)

    if step < len(questions):
        state["step"] = step
        send_message(chat_id, questions[step])
    else:
        result = grade_user("\n".join(state["answers"]), language)
        user_states[chat_id]["grade"] = result
        send_message(chat_id, result)
        save_result_to_sheet(username, language, state["answers"], result)
        user_states.pop(chat_id)

    return {"ok": True}
