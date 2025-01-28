from aiogram import executor

from data.config import ADMINS
from loader import dp,db
import middlewares, filters, handlers
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands
import asyncio
from random import choice
from datetime import datetime
import json
from functions import do_all
# CHANNELS = {'@Amirjon_Karimov_Blog':523, '@Amirjon_Karimov_Life':113}
# tugirlandi


async def on_startup(dispatcher):
    # Birlamchi komandaPlar (/star va /help)
    await db.create()
    try:
        await db.create_table_channel()
        await db.create_table_admins()
        await db.create_table_files()
        do_all()
    except Exception as err:
          print(err)
    # Get the user ID from the incoming update
    await set_default_commands(dispatcher)
    # Bot ishga tushgani haqida adminga xabar berish
    await on_startup_notify(dispatcher)

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)
    dp.middleware.setup()
    
