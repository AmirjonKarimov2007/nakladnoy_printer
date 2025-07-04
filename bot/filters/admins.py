from aiogram import types

from aiogram.dispatcher.filters import BoundFilter
from data.config import ADMINS
from loader import db

class IsSuperAdmin(BoundFilter):
    async def check(self, message: types.Message):
        user_id = message.from_user.id

        if str(user_id) in ADMINS:
            return True
        else:
            return False
        
class isYiguvchi(BoundFilter):
    async def check(self, message: types.Message):
        user_id = message.from_user.id
        user = await db.select_user(user_id=user_id)
        tekshirish = user[0]['yiguvchi']

        if tekshirish:
            return True
        else:
            return False
        
class IsAdmin(BoundFilter):
    async def check(self, message: types.Message):
        user_id = int(message.from_user.id)
        admin = await db.is_admin(user_id=user_id)
        if admin or str(user_id) in ADMINS: 
            return True
        else:
            return False
