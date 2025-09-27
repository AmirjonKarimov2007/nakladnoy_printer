from aiogram.utils.exceptions import BadRequest
import os
from aiogram.types import *
from filters.admins import IsAdmin
from loader import dp, bot
from functions import *
from data.config import ROOM_ID
import json

PER_PAGE = 10
product_pages = {}
checked_products = {}

STATUS_FILE = 'data/product_status.json'

def load_product_status():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {} 
    return {}


def save_product_status():
    checked_products_serializable = {
        str(key): value for key, value in checked_products.items()
    }

    with open('checked_products.json', 'w') as f:
        json.dump(checked_products_serializable, f)


checked_products = load_product_status()

def get_box_details(quantity, box_quant):
    if not isinstance(box_quant, int):
        return f"{quantity} шт."
    quantity = int(quantity)
    box_quant = int(box_quant)
    if box_quant == 0:
        return "0"
    full_boxes = quantity // box_quant
    remaining_items = quantity % box_quant
    if remaining_items == 0:
        return f"{full_boxes} коробка"
    elif full_boxes == 0:
        return f"{remaining_items} шт."
    else:
        return f"{full_boxes} коробка, {remaining_items} шт."

@dp.callback_query_handler(IsAdmin(), text_contains="preparation:", state='*')
async def order_products(call: CallbackQuery):
    await call.answer(cache_time=1)
    data = call.data.rsplit(":")
    deal_id = data[1]
    moment = data[2]
    user_id = call.from_user.id
    product_pages[user_id] = 0
    await show_order_products(call.message, deal_id, moment, user_id, 0)

@dp.callback_query_handler(IsAdmin(), lambda c: c.data.startswith("product_page:"))
async def change_product_page(callback: CallbackQuery):
    await callback.answer()
    _, deal_id, moment, page = callback.data.split(":")
    await show_order_products(callback.message, deal_id, moment, callback.from_user.id, int(page))


async def show_order_products(message: Message, deal_id: str, moment: str, user_id: int, page: int):
    order_info = await (
        get_today_order_info_by_deal_id(deal_id) if moment == 'today' else
        get_lastday_order_info_by_deal_id(deal_id) if moment == 'yesterday' else
        get_order_info_by_deal_id(deal_id)
    )

    products = order_info['order_products']
    total_pages = (len(products) - 1) // PER_PAGE + 1
    page = max(0, min(page, total_pages - 1))
    product_pages[user_id] = page

    start, end = page * PER_PAGE, (page + 1) * PER_PAGE
    markup = InlineKeyboardMarkup(row_width=1)

    for i, product in enumerate(products[start:end], start=1):
        idx = start + i
        check = " ✅" if checked_products.get((user_id, str(product['product_id']))) else ""
        markup.insert(InlineKeyboardButton(
            text=f"{check}{product['product_name']}",
            callback_data=f"product_detail:{deal_id}:{moment}:{product['product_id']}:{page}"
        ))

    nav_buttons = []
    person_name = order_info['person_name']
    total_amount = order_info['total_amount']
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Oldingi", callback_data=f"product_page:{deal_id}:{moment}:{page-1}"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("Keyingi ➡️", callback_data=f"product_page:{deal_id}:{moment}:{page+1}"))
    if nav_buttons:
        markup.row(*nav_buttons)
    if moment == 'today':
        markup.row(InlineKeyboardButton("🔙 Orqaga", callback_data=f"get_today_order:{deal_id}"))
    elif moment == 'yesterday':
        markup.row(InlineKeyboardButton("🔙 Orqaga", callback_data=f"get_yesterday_order:{deal_id}:{person_name[:10]}:{total_amount}"))

    text = (
        f"🛒 Buyurtma: #{deal_id}\n"
        f"👤 Mijoz: {order_info['person_name']}\n"
        f"🏢 Xona: {order_info['room_name']}\n"
        f"📅 Sana: {order_info['booked_date']}\n"
        f"💲 Jami: {order_info['total_amount']} {order_info['currency_code']}\n\n"
        f"📦 Mahsulotlar ({page+1}/{total_pages}):"
    )

    try:
        await message.edit_text(text, reply_markup=markup)
    except BadRequest as e:
        if "no text" in str(e):
            await message.delete()
            await bot.send_message(message.chat.id, text, reply_markup=markup)
        else:
            raise

@dp.callback_query_handler(IsAdmin(), lambda c: c.data.startswith("product_detail:"))
async def product_detail_handler(call: CallbackQuery):
    await call.answer()
    _, deal_id, moment, product_id, page = call.data.split(":")
    page = int(page)
    user_id = call.from_user.id

    order_info = await (
        get_today_order_info_by_deal_id(deal_id) if moment == 'today' else
        get_lastday_order_info_by_deal_id(deal_id) if moment == 'yesterday' else
        get_order_info_by_deal_id(deal_id)
    )
    product = next(p for p in order_info['order_products'] if str(p['product_id']) == product_id)

    image_path = f"rasmlar/{product_id}.jpg"
    exists = os.path.exists(image_path)
    is_checked = checked_products.get((user_id, product_id))
    status = "✅Olingan" if is_checked else ""

    caption = (
        f"📦 Mahsulot: {product['product_name']}\n"
        f"📊 Miqdor: {get_box_details(product['order_quant'], product['box_quant'])}\n"
        f"💰 Narxi: {product['product_price']}\n"
        f"🏠 Barcode: {product['product_barcode']}\n"
    )
    if is_checked:
        caption += f"status: {status}"

    markup = InlineKeyboardMarkup(row_width=2)
    markup.insert(
        InlineKeyboardButton("✅ Oldim", callback_data=f"product_checked:{deal_id}:{moment}:{product_id}:{page}")
    )
    markup.insert(
        InlineKeyboardButton("❌ Bekor qilish", callback_data=f"product_cancel:{deal_id}:{moment}:{product_id}:{page}")
    )
    markup.add(
        InlineKeyboardButton("🔙 Orqaga", callback_data=f"product_page:{deal_id}:{moment}:{page}")
    )

    if exists:
        with open(image_path, "rb") as img:
            if call.message.photo:
                media = InputMediaPhoto(media=img, caption=caption)
                await call.message.edit_media(media, reply_markup=markup)
            else:
                await call.message.delete()
                await bot.send_photo(call.message.chat.id, photo=img, caption=caption, reply_markup=markup)
    else:
        if call.message.photo:
            await call.message.delete()
            await bot.send_message(call.message.chat.id, caption, reply_markup=markup)
        else:
            await call.message.edit_text(caption, reply_markup=markup)



@dp.callback_query_handler(IsAdmin(), lambda c: c.data.startswith("product_checked:"))
async def product_checked_handler(call: CallbackQuery):
    await call.answer("✅ Mahsulot belgilandi")
    _, deal_id, moment, product_id, page = call.data.split(":")
    checked_products[(call.from_user.id, str(product_id))] = True
    save_product_status()  # Yangi: Holatni saqlash
    await show_order_products(call.message, deal_id, moment, call.from_user.id, int(page))

# Yangi: "Bekor qilish" holatini qayta ti   klash
@dp.callback_query_handler(IsAdmin(), lambda c: c.data.startswith("product_cancel:"))
async def product_cancel_handler(call: CallbackQuery):
    await call.answer("❌ Mahsulot bekor qilindi")
    _, deal_id, moment, product_id, page = call.data.split(":")
    if (call.from_user.id, str(product_id)) in checked_products:
        del checked_products[(call.from_user.id, str(product_id))]
    save_product_status()  # Yangi: Holatni saqlash
    await show_order_products(call.message, deal_id, moment, call.from_user.id, int(page))
