from data.config import ROOM_ID
import re
import os
from aiogram.types import * 
from keyboards.default.boglanish_button import *
from keyboards.inline.main_menu_super_admin import dates_markup
from loader import *
from filters.admins import *
from functions import *
from excelgenerator import print_excel_file,process_order, qrcode_generator
from data.config import ADMINS

@dp.message_handler(IsAdmin(),text="📄Profil Spiskalari",state='*')
async def spiskalar(message: types.Message):
    user = await db.select_user(user_id=message.from_user.id)
    user = user[0]
    saler_manager_id = user['saler_id']
    if saler_manager_id:
        markup = dates_markup(saler_manager_id)
        await message.answer(text="<b>📅Qaysi vaqtdagi buyurtmalarning ro'yxatini olmoqchisiz?</b>",reply_markup=markup)
    else:
        await message.answer("📅Sizning hisobingizga Saler Manager ID bog'lanmagan.ID ni olish uchun @Amirjon_Karimov ga murojaat qiling.")

@dp.callback_query_handler(IsAdmin(),text="back_to_date",state='*')
async def spiskalar(call: types.CallbackQuery):
    user = await db.select_user(user_id=call.from_user.id)
    user = user[0]
    saler_manager_id = user['saler_id']
    if saler_manager_id:
        markup = dates_markup(saler_manager_id)
        await call.message.edit_text(text="<b>📅Qaysi vaqtdagi buyurtmalarning ro'yxatini olmoqchisiz?</b>",reply_markup=markup)
    else:
        await call.message.edit_text("📅Sizning hisobingizga Saler Manager ID bog'lanmagan.ID ni olish uchun @Amirjon_Karimov ga murojaat qiling.")

@dp.callback_query_handler(IsAdmin(),text_contains="today:",state='*')
async def today_spiska(call: CallbackQuery):
    await call.answer("✅Bugungi spiskalar bo'limiga o'tdingiz ozgina sabr qiling.")
    saler_id = call.data.rsplit(":")[1]
    today_orders = await get_today_orders_by_manager(sales_manager_id=saler_id)
    markup = InlineKeyboardMarkup(row_width=1)
    for order in today_orders:
        deal_id=order['deal_id']
        person_name = order['person_name']
        total_amount = order['total_amount']
       
        markup.insert(InlineKeyboardButton(text=f"{person_name}-{total_amount}",callback_data=f"get_today_order:{deal_id}"))

    markup.insert(InlineKeyboardButton(text=f"⬅️Orqaga",callback_data=f'back_to_date'))
    try:
        await call.message.edit_text(f"<b>Sizning Bugungi Buyurtmalaringiz.</b>",reply_markup=markup)
    except:
        await call.message.edit_text(f"<b>Bugungi Buyurtmalaringiz ro'yxati!</b>",reply_markup=markup)

@dp.callback_query_handler(IsAdmin(),text_contains=f"get_today_order:",state='*')
async def get_order(call: CallbackQuery):
    
    deal_id = call.data.rsplit(":")[1]
    info = await get_today_order_info_by_deal_id(deal_id)
    client_id = info['person_name']
    text = f"<b>♻️Buyurtma haqida malumotlar.</b>\n\n"
    text += f"🆔Deal Id: <code>{deal_id}</code>\n"
    text += f"🪪 Client: <code>{info['person_name']}</code>\n"
    total_amount = info['total_amount']
    text += f"🪪 Client ID: <code>{client_id}</code>\n"
    text += f"💸Buyurtma Narx: <code>{total_amount}</code>\n"
    markup = InlineKeyboardMarkup(row_width=2)
    user = await db.select_user(user_id=call.from_user.id)
    qrcode =  qrcode_generator(deal_id)

    user = user[0]
    if user['yiguvchi']:
        markup.add(InlineKeyboardButton(text=f"⚙️Tayyorlash",callback_data=f"preparation:{deal_id}:today"))
    else:
        markup.insert(InlineKeyboardButton(text=f"🖨Chiqarish",callback_data=f"print_order:{deal_id}:today"))
        markup.add(InlineKeyboardButton(text=f"🖨 Narx Chiqarish",callback_data=f"print_price:{deal_id}:today"))
        markup.insert(InlineKeyboardButton(text=f"⚙️Tayyorlash",callback_data=f"preparation:{deal_id}:today"))
        markup.insert(InlineKeyboardButton(text=f"📥Yuklash",callback_data=f"download:{deal_id}:{client_id}:today"))
    
    try:
        with open(qrcode, 'rb') as photo:
            await call.message.edit_media(
                media=InputMediaPhoto(photo, caption=text, parse_mode="HTML"),
                reply_markup=markup
            )
    except:
        with open(qrcode, 'rb') as photo:
            await call.message.edit_media(
                media=InputMediaPhoto(photo, caption=text, parse_mode="HTML"),
                reply_markup=markup
            )

@dp.callback_query_handler(IsAdmin(),text_contains="yesterday:",state='*')
async def today_spiska(call: CallbackQuery):
    await call.answer(cache_time=1)
    saler_id = call.data.rsplit(":")[1]
    today_orders = await get_last_day_orders_by_manager(sales_manager_id=saler_id)
    markup = InlineKeyboardMarkup(row_width=1)
    for order in today_orders:
        deal_id=order['deal_id']
        person_name = order['person_name']
        total_amount = order['total_amount']
        person_id = order['person_id']
        markup.insert(InlineKeyboardButton(text=f"{person_name} - {total_amount}:{person_id}",callback_data=f"get_yerterday_order:{deal_id}:{person_name[:10]}:{total_amount}"))
    markup.insert(InlineKeyboardButton(text=f"⬅️Orqaga",callback_data=f'back_to_date'))
    await call.message.edit_text(f"<b>Sizning Kechangi Buyurtmalaringiz</b>",reply_markup=markup)

@dp.callback_query_handler(IsAdmin(),text_contains=f"get_yerterday_order:",state='*')
async def get_order(call: CallbackQuery):
    deal_id = call.data.rsplit(":")[1]
    client_name = call.data.rsplit(":")[2]
    total_amount = call.data.rsplit(":")[3]
    text = f"<b>♻️Buyurtma haqida malumotlar.</b>\n\n"
    text += f"🆔Deal Id: <code>{deal_id}</code>\n"
    text += f"🪪 Client: <code>{client_name}</code>\n"
    text += f"💸Buyurtma Narx: <code>{total_amount}</code>\n"
    button_title = next((button['text'] for row in call.message.reply_markup.inline_keyboard for button in row if button['callback_data'] == call.data), None)
    client_id = button_title.rsplit(":")[1]
    text += f"🪪 Client ID: <code>{client_id}</code>\n"
    markup = InlineKeyboardMarkup(row_width=2)
    user = await db.select_user(user_id=call.from_user.id)
    user = user[0]
    qrcode =  qrcode_generator(deal_id)
    
    if user['yiguvchi']:
        markup.add(InlineKeyboardButton(text=f"⚙️Tayyorlash",callback_data=f"preparation:{deal_id}:yesterday"))
    else:
        markup.insert(InlineKeyboardButton(text=f"🖨Chiqarish",callback_data=f"print_order:{deal_id}:yesterday"))
        markup.add(InlineKeyboardButton(text=f"🖨 Narx Chiqarish",callback_data=f"print_price:{deal_id}:yesterday"))
        markup.insert(InlineKeyboardButton(text=f"⚙️Tayyorlash",callback_data=f"preparation:{deal_id}:tyesterdayoday"))
        markup.insert(InlineKeyboardButton(text=f"📥Yuklash",callback_data=f"download:{deal_id}:{client_id}:tyesterdayoday"))
    
    with open(qrcode, 'rb') as photo:
        await call.message.edit_media(
            media=InputMediaPhoto(photo, caption=text, parse_mode="HTML"),
            reply_markup=markup
        )

@dp.callback_query_handler(IsAdmin(),text_contains=f"print_order:",state='*')
async def prin_order(call: CallbackQuery):
    deal_id = call.data.rsplit(":")[1]
    date = call.data.rsplit(":")[2]
    if date=='today':
        order = await process_order(deal_id=deal_id,output_path=deal_id,moment='today')
        if order:

            pechat = await print_excel_file(file_path=f"orders/{deal_id}.xlsx")
            if pechat:
                await call.answer("✅Chiqarish muvaffaqiyatli boshlandi",show_alert=True)
            else:
                await call.answer("❌Printerdan chiqmadi boshqattan urining.Printer yoniq ekaniga ishonch hosil qiling.",show_alert=True)
                

        else:
            await call.answer("❌Buyurtma Printerdan Chiqarish Amalga oshmadi",show_alert=True)
    if date=='yesterday':
        order = await process_order(deal_id=deal_id,output_path=deal_id,moment='yesterday')
        if order:
            pechat = await print_excel_file(file_path=f"orders/{deal_id}.xlsx")
            if pechat:
                await call.answer("✅Chiqarish muvaffaqiyatli boshlandi",show_alert=True)
            else:
                await call.answer("❌Printerdan chiqmadi boshqattan urining.Printer yoniq ekaniga ishonch hosil qiling.",show_alert=True)
        else:
            await call.answer("Buyurma bugungi kunda mavjud emas.")

PER_PAGE = 10
users_pages = {}  

@dp.message_handler(IsSuperAdmin(), text="📃Barcha Spiskalar", state="*")
@dp.message_handler(isYiguvchi(), text="📃Barcha Spiskalar", state="*")
async def spiskalar(message: types.Message):
    xabar = await message.answer(text='⏳')
    await get_today_orders()

    user_id = message.from_user.id
    users_pages[user_id] = 0 

    await show_orders(message, user_id, page=0)
    await xabar.delete()

SALERS = ['3814008','1862862','8477509']
async def show_orders(message: types.Message, user_id: int, page: int, call=None):
    
    orders = await today_all_orders()
    orders = [order for order in orders if order["room_id"] == str(ROOM_ID) and order["sales_manager_id"] in SALERS]
    if not orders:
        if call:
            await call.message.edit_text("Bugunda hech qanday buyurtmalar yo'q.")  
        else:
            await message.answer("Bugunda hech qanday buyurtmalar yo'q.")
    total_pages = (len(orders) - 1) // PER_PAGE + 1  
    if page < 0 or page >= total_pages:
        return  

    users_pages[user_id] = page  
    start = page * PER_PAGE
    end = start + PER_PAGE
    orders_page = orders[start:end] 

    markup = InlineKeyboardMarkup(row_width=2)
    for order in orders_page:
        deal_id = order["deal_id"]
        person_name = order["person_name"]
        sales_manager_name = order["sales_manager_name"]
        total_amount = order["total_amount"]
        person_id = order["person_id"]
        
        markup.add(
            InlineKeyboardButton(
                text=f"{sales_manager_name} - {person_name} - {total_amount}:{person_id}",
                callback_data=f"get_today_order:{deal_id}:{person_name[:10]}:{total_amount}",
            )
        )

    buttons = []
    if page > 0:
        buttons.append(InlineKeyboardButton(text="⬅️", callback_data=f"prev_page:{page}"))
    if page < total_pages - 1:
        buttons.append(InlineKeyboardButton(text="➡️", callback_data=f"next_page:{page}"))

    if buttons:
        markup.row(*buttons)

    text = f"<b>Sizning Bugungi Buyurtmalaringiz ({page+1}/{total_pages})</b>"

    if call:
        await call.message.edit_text(text, reply_markup=markup)  
    else:
        await message.answer(text, reply_markup=markup)

@dp.callback_query_handler(IsSuperAdmin(),lambda c: c.data.startswith("prev_page") or c.data.startswith("next_page"))
async def change_page(callback_query: types.CallbackQuery):
    await callback_query.answer(cache_time=1)
    user_id = callback_query.from_user.id
    data = callback_query.data.split(":")
    action = data[0]
    current_page = int(data[1])

    new_page = current_page - 1 if action == "prev_page" else current_page + 1
    await show_orders(callback_query.message, user_id, new_page, call=callback_query)  

def check_file_in_orders(file_name):
    file_path = os.path.join('orders', file_name)
    if os.path.isfile(file_path):
        return True
    else:
        return False

import json
@dp.callback_query_handler(IsAdmin(), text_contains="print_price:", state="*")
async def print_price(call: types.CallbackQuery):
    try:
        deal_id, date = call.data.split(":")[1:3]

        if date == 'today':
            order = await get_today_order_info_by_deal_id(deal_id_to_find=deal_id)
        elif date == 'yesterday':
            order = await get_lastday_order_info_by_deal_id(deal_id_to_find=deal_id)
        else:
            return await call.answer("❌ Sana noto‘g‘ri!")

        if order:
            await process_price(order['order_products'], call)
        else:
            await call.answer("❌Buyurtma Printerdan Chiqarish Amalga oshmadi")

    except Exception as e:
        print(e)


async def process_price(order_products, call):
    for order in order_products:
        product = await get_product_by_id(order['product_id'])
        barcode = order['product_barcode']
        # Barcode tekshirish
        if barcode == "null" or barcode==None:
            try:
                number = barcode.rsplit("/")
                barcode = number[1].rsplit(" ")[1]
                if not barcode.isdigit():
                    barcode = "0000000000000"
            except:
                barcode = "0000000000000"

        # Nomni 50 belgigacha qisqartirish
        name = product[0]['name'][-50:]
        price_uzs = int(product[0]['price_uzs'])
        price_uzs = "{:,}".format(price_uzs).replace(",", " ")
        price_usd = product[0]['price_usd']
        soni = 1 if int(order['sold_quant']) > 10 else int(order['sold_quant'])
        a = await print_barcode(
            word_name=call.message.message_id,
            data_to_encode=barcode,
            name=name,
            price=price_uzs,
            barcode_name=f'{call.id}.png',
            usd_price=price_usd,
            page=soni
        )
        if a:
            pass
        else:
            await call.message.answer(f"❌Narx chiqarib bo'lmadi. - {name} - {price_usd}")











@dp.callback_query_handler(IsAdmin(),text_contains=f"send_client:",state='*')
async def send_order(call: CallbackQuery):
    deal_id = call.data.rsplit(":")[1]
    client_id = call.data.rsplit(":")[2]
    user = await db.select_user(client_id=int(client_id))
    if user:
        order = check_file_in_orders(file_name=f"{deal_id}.xlsx")
        if order:
            await bot.send_document(chat_id=int(user[0]['user_id']),document=InputFile(f"orders/{deal_id}.xlsx"))
            await call.message.edit_text("<b>✅Mijozga Mahsulotlar ro'yxati yozilgan hujjatingizni muvvafaqiyatli yuborildi.</b>")
        else:
            await process_order(deal_id=deal_id,output_path=deal_id,moment=f'send:{deal_id}')
            await bot.send_document(chat_id=int(user[0]['user_id']),document=InputFile(f"orders/{deal_id}.xlsx"))
            await call.message.edit_text("<b>✅Mijozga Mahsulotlar ro'yxati yozilgan hujjatingizni muvvafaqiyatli yuborildi.</b>")
    else:
        await call.answer("❌Bu xaridor hali botimizga azo bo'lmagan.",show_alert=True)

@dp.callback_query_handler(IsAdmin(),text_contains=f"download:",state='*')
async def send_order(call: CallbackQuery):
    await call.message.delete()
    deal_id = call.data.rsplit(":")[1]
    user = await db.select_user(user_id=call.from_user.id)
    if user:
        await process_order(deal_id=deal_id,output_path=deal_id,moment=f'send:{deal_id}')
        await bot.send_document(chat_id=call.from_user.id,document=InputFile(f"orders/{deal_id}.xlsx"),caption="✅Fayl Muvaffaqiyatli yuklandi.")

    else:
        await call.answer("❌Bu Ishchi hali botimizga azo bo'lmagan.",show_alert=True)

@dp.message_handler(IsAdmin())
async def echo(message: Message):
    user = await db.select_user(user_id=message.from_user.id)
    user = user[0]

    if str(message.from_user.id) in ADMINS or user['yiguvchi']:
        await message.answer(text="Funksiyalarni Tanlang.",reply_markup=admin_orders_keyboard)
    else:
        await message.answer(text="Funksiyalarni Tanlang.",reply_markup=boglanish)

