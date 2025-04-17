
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_answers_and_generate(answers):
    joined_answers = "\n".join([f"{i+1}. {a}" for i, a in enumerate(answers)])
    system = (
        "Ты — эксперт по дизайну и карьерному развитию. Проанализируй ответы дизайнера и оцени его текущий грейд "
        "(Junior, Middle, Senior, Lead, Director). После этого предложи рекомендации и полезные материалы для роста "
        "до следующего уровня."
    )
    prompt = (
        f"Ответы пользователя:\n{joined_answers}\n\nСформулируй:\n"
        "1. Текущий грейд\n2. Основные сильные и слабые стороны\n"
        "3. Рекомендации по развитию\n4. Список полезных бесплатных материалов (ссылки и названия)"
    )

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    result = response.choices[0].message.content
    grade = "Неопределён"
    recommendations = ""
    materials = ""

    for line in result.split("\n"):
        if "грейд" in line.lower():
            grade = line.split(":")[-1].strip()
        elif "рекомендации" in line.lower():
            recommendations = line
        elif "материал" in line.lower():
            materials += line + "\n"

    return grade, recommendations.strip(), materials.strip()
