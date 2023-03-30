from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def send_phone_kb():
    send_phone_kb = ReplyKeyboardMarkup(resize_keyboard=True)
    send_phone_kb.add(KeyboardButton(text="Отправить номер телефона", request_contact=True))

    return send_phone_kb

def choose_ai_kb():
    choose_ai_kb = InlineKeyboardMarkup(row_width=1)
    buttons = [
        InlineKeyboardButton(text="ChatGPT-3.5", callback_data="gpt_button")
    ]
    choose_ai_kb.add(*buttons)

    return choose_ai_kb
