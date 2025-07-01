from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from filters.admins import IsSuperAdmin
from functions import *
from loader import dp, bot, db
from data.config import ROOM_ID
from filters.admins import IsAdmin

PER_PAGE = 10
users_pages = {}
selected_orders = {}  # Foydalanuvchi tanlagan buyurtmalar

@dp.message_handler(IsAdmin(), commands="rasxod", state="*")
async def spiskalar(message: types.Message):
    xabar = await message.answer(text='⏳')
    await get_today_orders()

    user_id = message.from_user.id
    users_pages[user_id] = 0

    await show_orders(message, user_id, page=0)
    await xabar.delete()

async def show_orders(message: types.Message, user_id: int, page: int, call=None):
    orders = await today_all_orders()
    orders = [order for order in orders if order["room_id"] == str(ROOM_ID)]

    if not orders:
        text = "Bugunda hech qanday buyurtmalar yo'q."
        if call:
            await call.message.edit_text(text)
        else:
            await message.answer(text)
        return

    total_pages = (len(orders) - 1) // PER_PAGE + 1
    users_pages[user_id] = page

    start = page * PER_PAGE
    end = start + PER_PAGE
    orders_page = orders[start:end]

    markup = InlineKeyboardMarkup(row_width=2)
    selected = selected_orders.get(user_id, set())

    for order in orders_page:
        deal_id = order["deal_id"]
        person_name = order["person_name"]
        sales_manager_name = order["sales_manager_name"]
        total_amount = order["total_amount"]
        person_id = order["person_id"]

        is_selected = "✅ " if deal_id in selected else ""
        btn_text = f"{is_selected}{sales_manager_name} - {person_name} - {total_amount}:{person_id}"

        markup.add(
            InlineKeyboardButton(
                text=btn_text,
                callback_data=f"create_consumption:{deal_id}:{person_name[:10]}:{total_amount}"
            )
        )
    
    buttons = []
    if page > 0:
        buttons.append(InlineKeyboardButton(text="⬅️", callback_data=f"consumption_prev_page:{page}"))
    if page < total_pages - 1:
        buttons.append(InlineKeyboardButton(text="➡️", callback_data=f"consumption_next_page:{page}"))
    if buttons:
        markup.row(*buttons)
    if selected:
        markup.add(InlineKeyboardButton(text="📤 Chiqarish", callback_data="export_selected_orders"))
    text = f"<b>Sizning Bugungi Buyurtmalaringiz ({page+1}/{total_pages})</b>"
    if call:
        await call.message.edit_text(text, reply_markup=markup)
    else:
        await message.answer(text, reply_markup=markup)





@dp.callback_query_handler(IsAdmin(), lambda c: c.data.startswith("create_consumption:"))
async def toggle_order_selection(call: types.CallbackQuery):
    _, deal_id, person_name, total_amount = call.data.split(":")

    user_id = call.from_user.id 
    selected = selected_orders.setdefault(user_id, set())

    if deal_id in selected:
        selected.remove(deal_id)
    else:
        selected.add(deal_id)

    await show_orders(call.message, user_id, users_pages.get(user_id, 0), call=call)

@dp.callback_query_handler(IsAdmin(), lambda c: c.data.startswith("consumption_prev_page") or c.data.startswith("consumption_next_page"))
async def change_page(callback_query: types.CallbackQuery):
    await callback_query.answer(cache_time=1)
    user_id = callback_query.from_user.id
    data = callback_query.data.split(":")
    action = data[0]
    current_page = int(data[1])

    new_page = current_page - 1 if action == "consumption_prev_page" else current_page + 1
    await show_orders(callback_query.message, user_id, new_page, call=callback_query)


import openpyxl
from openpyxl.styles import Font
from io import BytesIO
from excelgenerator import update_excel_with_products


@dp.callback_query_handler(IsAdmin(), lambda c: c.data == "export_selected_orders")
async def export_selected_orders(call: types.CallbackQuery):
    user_id = call.from_user.id
    selected = selected_orders.get(user_id, set())
    if not selected:
        await call.answer("Hech narsa tanlanmagan.", show_alert=True)
        return

    products = []
    for deal_id in selected:
        result = await get_selected_orders(deal_id=str(deal_id))
        if result and "order" in result:
            for order in result["order"]:
                for p in order.get("order_products", []):
                    products.append({
                        "product_code": p.get("product_code", "Noma'lum"),
                        "order_quant": int(float(p.get("order_quant", 0))),
                        "product_price": int(float(p.get("product_price", 0)))
                    })

    if not products:
        await call.answer("Tanlangan buyurtmalarda mahsulotlar topilmadi.", show_alert=True)
        return

    # Excel faylga yozish
    file_path = r"C:\Users\alfatech.uz\Documents\nakladnoy_printer\bot\rasxod.xlsx"
    output_file = update_excel_with_products(file_path, products)

    # Yuborish
    await call.message.answer_document(open(output_file, "rb"), caption="✅ Tanlangan buyurtmalar ro'yxati")

    # Tozalash
    selected_orders[user_id] = set()
