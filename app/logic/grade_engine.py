
from openai import OpenAI
from app.logic.prompts import GRADE_PROMPT_TEMPLATE

client = OpenAI()

def grade_user_from_history(history: list[str]) -> dict:
    prompt = GRADE_PROMPT_TEMPLATE.format(history="\n".join(history))

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
        )
        if response.choices:
            content = response.choices[0].message.content.strip()
        else:
            content = "Не удалось определить грейд."

        # Можно позже парсить content, пока — как текст
        return {
            "grade": "определяется GPT",
            "recommendations": ["Прокачать навык наставничества", "Углубить влияние на продукт"],
            "materials": ["https://example.com/article1", "https://example.com/book"]
        }
    except Exception as e:
        print("❌ Ошибка GPT (grade_user_from_history):", e)
        return {
            "grade": "Ошибка",
            "recommendations": [],
            "materials": []
        }
