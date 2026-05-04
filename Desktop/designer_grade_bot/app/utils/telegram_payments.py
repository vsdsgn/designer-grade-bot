import os

def get_payment_button(language="en"):
    title = "💫 Купить доступ за $1" if language == "ru" else "💫 Unlock for $1"
    return [{
        "text": title,
        "pay": True
    }]

# Текст инвойса и описание покупки
def get_payment_payload():
    return {
        "title": "Доступ к тесту дизайнера",
        "description": "Повторный запуск теста. Оплата через Telegram Stars.",
        "currency": "USD",
        "prices": [{"label": "Повторный запуск", "amount": 100}],  # $1 = 100 cents
        "payload": "designer_test_unlock"
    }
