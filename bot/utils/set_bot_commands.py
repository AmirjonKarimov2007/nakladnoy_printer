from aiogram import types


async def set_default_commands(dp):
    await dp.bot.set_my_commands(
        [
            types.BotCommand("start", "Botni ishga tushurish"),
            types.BotCommand("help", "Yordam"),
            types.BotCommand("rasxod", "Bu bo'limda spiskalarni bazadan chiqarib yuborishingiz mumkin!"),
            types.BotCommand("register", "Sotuvchi uchun ro'yxatdan o'tish uchun funksiya."),
        ]
    )


