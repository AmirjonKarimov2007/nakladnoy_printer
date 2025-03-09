from aiogram import types
from aiogram.types import ReplyKeyboardRemove,ReplyKeyboardMarkup,KeyboardButton
from loader import dp

admin_orders_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
        KeyboardButton(text="📃Barcha Spiskalar"),
        ],
        [
        KeyboardButton(text="📄Profil Spiskalari")
        ]
    ],
    resize_keyboard=True
)
boglanish = ReplyKeyboardMarkup(
    keyboard=[
        [
        KeyboardButton(text="📄Profil Spiskalari")
        ]
    ],
    resize_keyboard=True
)

check = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="✅Ha"),
            KeyboardButton(text="❌Yo'q")
        ],
    ],
    resize_keyboard=True
)
