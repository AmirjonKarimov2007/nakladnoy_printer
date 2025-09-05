from loader import dp,db,bot
from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from filters.users import IsGroup,IsBlocked
from aiogram.types import InputFile
from filters.admins import IsAdmin
import ssl
import aiohttp
import pytz
from datetime import datetime,timedelta
import json
from data.config import USD
async def get_order_for_balans():

    uzbekistan_tz = pytz.timezone('Asia/Tashkent')
    today = datetime.now(uzbekistan_tz)
    
    begin_date = today.replace(day=1).strftime('%d.%m.%Y')
    
    end_date = today.strftime('%d.%m.%Y')
    url = "https://smartup.online/b/trade/txs/tdeal/order$export"
    
    auth = aiohttp.BasicAuth('ramazon14@falcon', '111222')

    headers = { 
        'filial_id': '5012602',
        'project_code': 'trade',
    }

    data = {
        
        "filial_codes": [{"filial_code": "5012602"}],
        "statuses":["B#N"],
      
        "begin_deal_date": begin_date,
        "end_deal_date": end_date,
        }

    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE  

    async with aiohttp.ClientSession(auth=auth) as session:
        async with session.post(url, json=data, headers=headers, ssl=ssl_context) as response:
            text = await response.text()  # Javobni text sifatida olish
            
            
            if response.status == 200:
                try:
                    json_data = json.loads(text)  # JSON ga o'girishga harakat qilish
                    
                    
                    return json_data

                except json.JSONDecodeError:
                    return False
            else:
                return False  
            
async def get_order_for_balans_last_month():
    uzbekistan_tz = pytz.timezone('Asia/Tashkent')
    today = datetime.now(uzbekistan_tz)
    
    # O'tgan oy boshlanishi va tugashi
    last_month_end = today.replace(day=1) - timedelta(days=1)
    last_month_start = last_month_end.replace(day=1)

    # String formatga o'tkazish
    begin_date = last_month_start.strftime('%d.%m.%Y')
    end_date = last_month_end.strftime('%d.%m.%Y')
    url = "https://smartup.online/b/trade/txs/tdeal/order$export"
    
    auth = aiohttp.BasicAuth('ramazon14@falcon', '111222')

    headers = { 
        'filial_id': '5012602',
        'project_code': 'trade',
    }

    data = {
        "filial_codes": [{"filial_code": "5012602"}],
        "statuses": ["B#N"],
        "begin_deal_date": begin_date,
        "end_deal_date": end_date,
    }

    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    async with aiohttp.ClientSession(auth=auth) as session:
        async with session.post(url, json=data, headers=headers, ssl=ssl_context) as response:
            text = await response.text()
            
            if response.status == 200:
                try:
                    json_data = json.loads(text)
                    return json_data
                except json.JSONDecodeError:
                    return False
            else:
                return False
            

@dp.message_handler(text="💰Balans", state='*')
async def balans(message: types.Message):
    user_id = message.from_user.id
    user = await db.is_user(user_id=message.from_user.id)

    # Bugungi oyning sanalari
    uzbekistan_tz = pytz.timezone('Asia/Tashkent')
    today = datetime.now(uzbekistan_tz)
    begin_date = today.replace(day=1).strftime('%d.%m.%Y')
    end_date = today.strftime('%d.%m.%Y')

    loading_msg = await message.answer("⏳ Hisob-kitob qilinyapti, biroz kuting...")

    orders = await get_order_for_balans()
    jami_uzs_pullar = 0
    jami_usd_pullar = 0
    
    for order in orders["order"]:
        moneytype = order['currency_code']
        if int(order["sales_manager_id"]) == user[0]['saler_id'] and int(order['room_code'])!=1:
            money = float(order['total_amount'])
            if int(moneytype) == 860:
                jami_uzs_pullar += money
            else:
                jami_usd_pullar += money

    # formatlash
    uzs_str = "{:,.0f}".format(jami_uzs_pullar).replace(",", " ")
    usd_str = "{:,.2f}".format(jami_usd_pullar).replace(",", " ")

    # jami USD hisoblash
    uzs_to_usd = jami_uzs_pullar / USD
    jami_usd_obshiy = uzs_to_usd + jami_usd_pullar
    jami_usd_str = "{:,.2f}".format(jami_usd_obshiy).replace(",", " ")

    await loading_msg.edit_text(
        f"<b>🗓 Hisob-kitob davri:</b> {begin_date} ➝ {end_date}\n\n"
        f"<b>💰 Sizning balansingiz:</b>\n"
        f"🇺🇿 {uzs_str} so'm\n"
        f"💸 {usd_str} USD\n\n"
        f"🌍 <u>Umumiy ekvivalent:</u> 💵 <b>{jami_usd_str} USD</b>"
    )


@dp.message_handler(text="🗓 Otgan oy", state='*')
async def get_last_month_salary(message: types.Message):
    user_id = message.from_user.id
    user = await db.is_user(user_id=message.from_user.id)

    uzbekistan_tz = pytz.timezone('Asia/Tashkent')
    today = datetime.now(uzbekistan_tz)
    last_month_end = today.replace(day=1) - timedelta(days=1)
    last_month_start = last_month_end.replace(day=1)

    begin_date = last_month_start.strftime('%d.%m.%Y')
    end_date = last_month_end.strftime('%d.%m.%Y')

    loading_msg = await message.answer("⏳ Hisob-kitob qilinyapti, biroz kuting...")

    orders = await get_order_for_balans_last_month()
    jami_uzs_pullar = 0
    jami_usd_pullar = 0
    
    for order in orders["order"]:
        moneytype = order['currency_code']
        if int(order["sales_manager_id"]) == user[0]['saler_id'] and int(order['room_code'])!=1:
            money = float(order['total_amount'])
            if int(moneytype) == 860:
                jami_uzs_pullar += money
            else:
                jami_usd_pullar += money

    uzs_str = "{:,.0f}".format(jami_uzs_pullar).replace(",", " ")
    usd_str = "{:,.2f}".format(jami_usd_pullar).replace(",", " ")

    uzs_to_usd = jami_uzs_pullar / USD
    jami_usd_obshiy = uzs_to_usd + jami_usd_pullar
    jami_usd_str = "{:,.2f}".format(jami_usd_obshiy).replace(",", " ")

    await loading_msg.edit_text(
        f"<b>🗓 Hisob-kitob davri:</b> {begin_date} ➝ {end_date}\n\n"
        f"<b>💰 Sizning balansingiz:</b>\n"
        f"🇺🇿 {uzs_str} so'm\n"
        f"💸 {usd_str} USD\n\n"
        f"🌍 <u>Umumiy ekvivalent:</u> 💵 <b>{jami_usd_str} USD</b>"
    )

@dp.message_handler(text="🔍 Filterlash", state='*')
async def get_last_month_salary(message: types.Message):
    pass