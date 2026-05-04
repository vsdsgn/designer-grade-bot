texts = {
    "greeting": {
        "ru": (
            "👋 Привет, {name}! Рад видеть тебя здесь.

"
            "Этот бот поможет тебе понять, на каком ты уровне как дизайнер — без давления, оценок "на показ", просто честный и добрый фидбек. "
            "Тест короткий, пройти можно за 5–7 минут.

"
            "🎁 Первый раз — бесплатно.
"
            "📌 Дальше — $1 через Telegram Stars.

"
            "📄 В конце ты получишь PDF с визуализацией твоего грейда, рекомендациями по развитию и подборкой полезных материалов.

"
            "Нажми кнопку ниже, когда будешь готов 🙂"
        ),
        "en": (
            "👋 Hi, {name}! Great to see you here.

"
            "This bot will help you reflect on your design level — no stress, no judgment, just honest and thoughtful feedback. "
            "The test is short — around 5–7 minutes.

"
            "🎁 First run is free.
"
            "📌 After that — $1 via Telegram Stars.

"
            "📄 At the end, you'll receive a PDF with a visual summary of your current grade, development tips, and a selection of resources.

"
            "Tap the button below when you’re ready 🙂"
        )
    },
    "start_button": {
        "ru": "🚀 Начать тест",
        "en": "🚀 Start the test"
    },
    "reset_message": {
        "ru": "🔄 Сессия сброшена. Напиши /start, чтобы пройти тест заново.",
        "en": "🔄 Session reset. Type /start to retake the test."
    },
    "language_prompt": {
        "ru": "🌍 Напиши язык, на котором хочешь продолжить (например: Русский, English)",
        "en": "🌍 Please type the language you'd like to use (e.g., English, Русский)"
    },
    "feedback_prompt": {
        "ru": "💬 Напиши свой отзыв или пожелание прямо здесь, и я передам его команде. Спасибо! 🙏",
        "en": "💬 You can write your feedback or suggestion here, and I’ll forward it to the team. Thank you! 🙏"
    },
    "no_result": {
        "ru": "❗ Пока нет результатов. Напиши /start, чтобы пройти тест.",
        "en": "❗ No results yet. Type /start to take the test."
    },
    "last_grade": {
        "ru": "📊 Последний определённый грейд: {grade}",
        "en": "📊 Last detected grade: {grade}"
    },
    "language_not_recognized": {
        "ru": "❌ Язык не распознан. Попробуй снова (например: Русский, English)",
        "en": "❌ Language not recognized. Please try again (e.g., English, Русский)"
    },
    "please_start": {
        "ru": "❗ Пожалуйста, начни с /start.",
        "en": "❗ Please start with /start."
    }
}

def get_text(key, lang="en", **kwargs):
    template = texts.get(key, {}).get(lang, texts[key]["en"])
    return template.format(**kwargs)
