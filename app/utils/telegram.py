import requests
import os
import json

TELEGRAM_API = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}"

def send_message(chat_id, text):
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    response = requests.post(url, json=payload)
    if not response.ok:
        print("⚠️ Ошибка при отправке сообщения:", response.text)

def send_document(chat_id, file_path):
    url = f"{TELEGRAM_API}/sendDocument"
    with open(file_path, "rb") as f:
        files = {"document": f}
        data = {"chat_id": chat_id}
        response = requests.post(url, data=data, files=files)
        if not response.ok:
            print("⚠️ Ошибка при отправке документа:", response.text)

def delete_inline_keyboard(chat_id, message_id):
    url = f"{TELEGRAM_API}/editMessageReplyMarkup"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "reply_markup": json.dumps({"inline_keyboard": []})
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
    except Exception as e:
        print(f"Ошибка при удалении клавиатуры: {e}")