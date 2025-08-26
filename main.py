from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import aiohttp
import pytz
import ssl
import json
from datetime import datetime

# Tashkent vaqti
uzbekistan_tz = pytz.timezone('Asia/Tashkent')
today = datetime.now(uzbekistan_tz).strftime('%d.%m.%Y')

app = FastAPI()

# Static va templates ulash
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# API dan ma’lumot olish
async def get_selected_orders(deal_id: str):
    url = "https://smartup.online/b/trade/txs/tdeal/order$export"
    auth = aiohttp.BasicAuth('ramazon14@falcon', '111222')
    headers = {
        'filial_id': '5012602',
        'project_code': 'trade',
    }
    data = {
        "filial_codes": [{"filial_code": "5012602"}],
        "deal_id": deal_id,
        "statuses": [],
        "begin_deal_date": "",
        "end_deal_date": "",
    }

    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    try:
        async with aiohttp.ClientSession(auth=auth) as session:
            async with session.post(url, json=data, headers=headers, ssl=ssl_context) as response:
                if response.status != 200:
                    return None
                text = await response.text()
                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    return None
    except Exception as e:
        print(f"❌ API bilan muammo: {e}")
        return None


# Asosiy sahifa
@app.get("/", response_class=HTMLResponse)
async def order_page(request: Request, order_id: str = None):
    if not order_id:
        return templates.TemplateResponse("order.html", {
            "request": request,
            "order": None
        })

    order = await get_selected_orders(order_id)

    # himoya: agar order topilmasa yoki noto‘g‘ri bo‘lsa
    try:
        order_data = order.get("order", [])
        if not order_data:
            order_data = None
        else:
            order_data = order_data[0]
    except Exception:
        order_data = None

    return templates.TemplateResponse("order.html", {
        "request": request,
        "order": order_data
    })
