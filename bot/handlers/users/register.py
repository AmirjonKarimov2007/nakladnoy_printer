from aiogram.types import *
from data.config import *
from loader import *
from states.admin_state import SuperAdminState
from filters.admins import IsAdmin
from functions import *




@dp.message_handler(IsAdmin(),commands='register',state='*')
async def register_user(message: Message):
    await message.answer(text=f"Iltimos {message.from_user.first_name},Smartup tomindan berilgan sotuvchilik idyingizni kiriting.")
    await SuperAdminState.SUPER_ADMIN_REGISTER_STATE.set()  
from aiogram.dispatcher import FSMContext
@dp.message_handler(IsAdmin(),content_types=ContentType.TEXT,state=SuperAdminState.SUPER_ADMIN_REGISTER_STATE)
async def user_regisration(message: Message,state:FSMContext):
    xabar = await message.answer('ID tekshiriliyapdi kuting...')
    saler_id = message.text
    if saler_id.isdigit():
        
        check= await check_user_saler_id(saler_id)
        if check:
            await db.update_saler_id(user_id=message.from_user.id,saler_id=int(saler_id))
            await xabar.delete()
            await message.answer("✅Siz muvaffaqiyatli ro'yxatdan o'tdingiz.")
            await state.finish()
        else:
           await message.answer("❌Siz notugri ID yubording. boshqattan urinib ko'ring. /register")
           await state.finish()
    else:
        await message.answer("ID faqat raqamlardan iborat bo'lishi kerak.")
