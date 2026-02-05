# Designer Grade Bot

Telegram-бот для оценки грейда дизайнера на базе FastAPI + OpenAI.

## Запуск локально

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Переменные окружения

- TELEGRAM_BOT_TOKEN
- TELEGRAM_WEBHOOK_SECRET
- OPENAI_API_KEY
- OPENAI_MODEL (например, gpt-4.1)
- PUBLIC_URL (https://<service>.up.railway.app)
- AUTO_SET_WEBHOOK=true
- DATA_DIR=/data

## Railway

1. Подключите репозиторий.
2. Добавьте Volume и примонтируйте к /data.
3. Задайте переменные окружения (см. выше).
4. Сделайте Redeploy, чтобы вебхук установился автоматически.
