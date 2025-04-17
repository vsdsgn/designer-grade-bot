
from openai import OpenAI
from app.logic.prompts import BASE_PROMPT

client = OpenAI()

def get_next_question(session: dict) -> str:
    history = session.get("messages", [])
    messages = [{"role": "system", "content": BASE_PROMPT}]

    for answer in history:
        messages.append({"role": "user", "content": answer})

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
        )
        if response.choices:
            return response.choices[0].message.content.strip()
        else:
            return "Что-то пошло не так. Попробуй снова."
    except Exception as e:
        print("❌ Ошибка GPT (get_next_question):", e)
        return "Произошла ошибка. Попробуй позже."
