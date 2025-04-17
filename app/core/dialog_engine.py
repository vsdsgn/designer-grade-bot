from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

BASE_PROMPT = (
    "Ты — опытный ментор-дизайнер. Твоя задача — определить грейд собеседника (Junior, Middle, Senior, Lead, Director) "
    "на основе диалога из 6–10 вопросов. Каждый вопрос должен раскрывать навыки, мышление и подход кандидата. "
    "Задавай вопросы по одному. Отвечай только вопросом, не добавляй комментариев. Формулируй их просто и понятно."
)

def get_next_question(session):
    history = session.get("answers", [])
    messages = [{"role": "system", "content": BASE_PROMPT}]
    
    for answer in history:
        messages.append({"role": "user", "content": answer})
    
    messages.append({"role": "assistant", "content": "Следующий вопрос?"})
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return "Произошла ошибка при генерации вопроса. Попробуй ещё раз."