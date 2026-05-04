import os

# Здесь можно будет добавить проверку оплаты, флаг первого запуска и т.д.
# Пока храним в памяти, в будущем можно заменить на базу

user_access = {}

def has_access(chat_id):
    state = user_access.get(chat_id, {"free_used": False, "paid": False})
    return not state["free_used"] or state["paid"]

def mark_used(chat_id):
    if chat_id not in user_access:
        user_access[chat_id] = {"free_used": True, "paid": False}
    else:
        user_access[chat_id]["free_used"] = True

def mark_paid(chat_id):
    if chat_id not in user_access:
        user_access[chat_id] = {"free_used": True, "paid": True}
    else:
        user_access[chat_id]["paid"] = True

def reset_access(chat_id):
    if chat_id in user_access:
        user_access[chat_id]["paid"] = False
