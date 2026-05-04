def get_questions(language: str):
    questions = {
        "en": [
            "1️⃣ Tell me a bit about your design journey. Where did you start and what are you doing now?",
            "2️⃣ What kind of tasks do you enjoy the most? And which ones drain your energy?",
            "3️⃣ How do you usually approach solving product problems?",
            "4️⃣ Which tools do you use regularly — and for what?",
            "5️⃣ Have you ever done user research yourself? How did you go about it?",
            "6️⃣ What’s your process when working with developers and PMs? What helps you stay aligned?",
            "7️⃣ Do you have experience mentoring someone or leading a team?",
            "8️⃣ Any projects you’re especially proud of? What makes them special to you?",
            "9️⃣ What’s something you’d really like to grow in as a designer right now?",
            "🔟 If you had to grade yourself — what level would you give and why?"
        ],
        "ru": [
            "1️⃣ Расскажи немного о своём опыте. С чего ты начинал в дизайне и чем занимаешься сейчас?",
            "2️⃣ Какие задачи тебе особенно нравятся? Есть те, которые наоборот — утомляют?",
            "3️⃣ Как ты обычно подходишь к решению продуктовой задачи?",
            "4️⃣ Какие инструменты ты используешь чаще всего — и зачем?",
            "5️⃣ Были ли у тебя ситуации, когда ты сам проводил исследование? Как ты это делал?",
            "6️⃣ Как ты работаешь с разработчиками и менеджерами? Что помогает быть на одной волне?",
            "7️⃣ Был ли у тебя опыт наставничества, обучения кого-то или ведения команды?",
            "8️⃣ Есть ли у тебя задачи или проекты, которыми ты особенно гордишься? Почему?",
            "9️⃣ Что ты хочешь прокачать в себе в ближайшее время?",
            "🔟 Если бы ты сам себя грейдил — какой бы грейд ты себе поставил и почему?"
        ]
    }
    return questions.get(language, questions["en"])

def get_intro(language: str) -> str:
    intros = {
        "en": (
            "👋 Hi there! I’ll help you reflect on your current level as a designer.\n\n"
            "💡 To get the most accurate and useful feedback — just write naturally, like we're having coffee and chatting about your experience.\n\n"
            "Some tips:\n"
            "— take your time and write in your own words\n"
            "— share real-life examples\n"
            "— no need to impress — just be yourself\n\n"
            "Ready? Let’s go!"
        ),
        "ru": (
            "👋 Привет! Я помогу тебе оценить твой текущий грейд как дизайнера.\n\n"
            "💡 Чтобы результат был точным и полезным — просто рассказывай от себя, как если бы мы с тобой сидели за чашкой кофе и говорили о твоём опыте.\n\n"
            "Вот пара советов:\n"
            "— не спеши, пиши развёрнуто\n"
            "— приводи реальные примеры\n"
            "— не старайся “казаться круче” — лучше будь собой\n\n"
            "Готов? Поехали!"
        )
    }
    return intros.get(language, intros["en"])
