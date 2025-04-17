
import os
import httpx

TELEGRAM_API_URL = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}"

async def send_message(chat_id, text, reply_markup=None):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(url, json=payload)
            r.raise_for_status()
    except Exception as e:
        print("❌ Ошибка при отправке сообщения:", e)

async def send_document(chat_id, file_path):
    url = f"{TELEGRAM_API_URL}/sendDocument"
    try:
        with open(file_path, "rb") as file:
            files = {"document": file}
            data = {"chat_id": chat_id}
            async with httpx.AsyncClient() as client:
                r = await client.post(url, data=data, files=files)
                r.raise_for_status()
    except Exception as e:
        print("❌ Ошибка при отправке документа:", e)

async def delete_inline_keyboard(chat_id, message_id):
    url = f"{TELEGRAM_API_URL}/editMessageReplyMarkup"
    payload = {"chat_id": chat_id, "message_id": message_id, "reply_markup": {}}
    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(url, json=payload)
            r.raise_for_status()
    except Exception as e:
        print("❌ Ошибка при удалении inline-кнопки:", e)
