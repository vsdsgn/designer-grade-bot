# Designer Grade Bot

Telegram-бот для оценки грейда дизайнеров цифровых продуктов и интерфейсов.

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
- DATABASE_URL (опционально; если не задан — используется локальное JSON‑хранилище)

## Хранилище без Postgres

Если Postgres не подключен, бот сохраняет:
- статусы пользователей в `DATA_DIR/user_state.json`
- фидбек в `DATA_DIR/feedback.json`

Для постоянного хранения подключите Volume и примонтируйте к `/data`.

## Railway

1. Подключите репозиторий.
2. Добавьте Volume и примонтируйте к /data.
3. Задайте переменные окружения.
4. Redeploy для установки webhook.
