import os
from openai import OpenAI
from dotenv import load_dotenv
from app.utils.grade_feedback import grade_recommendations

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_grade_from_response(response_text):
    grades = ["Junior", "Middle", "Senior", "Lead", "Director"]
    for grade in grades:
        if grade.lower() in response_text.lower():
            return grade
    return "Unknown"

def grade_user(answers_text, language="en"):
    system_prompt = {
        "en": "You're a design mentor who gives warm, motivating, realistic feedback and assigns a level from Junior to Director based on answers.",
        "ru": "Ты дизайн-ментор. Дай тёплый, мотивирующий, честный фидбек. Присвой грейд от Junior до Director на основе ответов."
    }

    prompt = [
        {"role": "system", "content": system_prompt.get(language, system_prompt["en"])},
        {"role": "user", "content": answers_text}
    ]

    response = client.chat.completions.create(
        model="gpt-4",
        messages=prompt,
        temperature=0.7
    )

    reply = response.choices[0].message.content
    grade = extract_grade_from_response(reply)

    # Добавим рекомендации
    rec = grade_recommendations.get(grade, {})
    advice = rec.get("advice", {}).get(language)
    if advice:
        reply += f"\n\n{advice}"

    return reply
