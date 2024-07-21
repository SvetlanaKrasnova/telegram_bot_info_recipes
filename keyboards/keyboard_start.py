from aiogram import types

kb = [[
    types.KeyboardButton(text="Команды"),
    types.KeyboardButton(text="Описание бота"),
], ]

keyboard = types.ReplyKeyboardMarkup(
    keyboard=kb,
    resize_keyboard=True,
)
