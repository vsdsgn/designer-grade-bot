import os
import json
import re
from openai import OpenAI

openai_api_key = os.getenv("OPENAI_API_KEY")

def grade_user_from_history(history: list[str]) -> dict:
    with open("data/levels.json", "r") as f:
        levels = json.load(f)

    levels_text = "\n".join(
        [f"{lvl['level']}: {lvl['description']}" for lvl in levels]
    )
    prompt = f"""
Ты — эксперт по оценке дизайнеров. На основе истории ответов пользователя:
{history}

И матрицы уровней:
{levels_text}

Определи текущий уровень пользователя. Также предложи, какие навыки ему развивать, чтобы перейти на следующий уровень. Верни ответ в формате JSON:
{{
    "grade": "Senior",
    "next_step": "Lead",
    "recommendations": ["Прокачать навык наставничества", "Углубить влияние на продукт"],
    "materials": ["https://example.com/article1", "https://example.com/book"]
}}
"""

    client = OpenAI(api_key=openai_api_key)
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    if response.choices:
    content = response.choices[0].message.content
else:
    content = "Ошибка генерации ответа"
    json_match = re.search(r"\{.*\}", content, re.DOTALL)
    return json.loads(json_match.group()) if json_match else {"error": "Invalid GPT output"}