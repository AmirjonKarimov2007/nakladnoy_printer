from flask import Flask, render_template, request
import requests
import ssl
import json
import pytz
from datetime import datetime

# Tashkent vaqti
uzbekistan_tz = pytz.timezone('Asia/Tashkent')
today = datetime.now(uzbekistan_tz).strftime('%d.%m.%Y')

app = Flask(__name__, template_folder="templates", static_folder="static")


# API dan ma’lumot olish
def get_selected_orders(deal_id: str):
    url = "https://smartup.online/b/trade/txs/tdeal/order$export"
    auth = ('ramazon14@falcon', '111222')
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

    try:
        response = requests.post(url, json=data, headers=headers, auth=auth, verify=False)
        if response.status_code != 200:
            return None
        try:
            return response.json()
        except json.JSONDecodeError:
            return None
    except Exception as e:
        print(f"❌ API bilan muammo: {e}")
        return None


@app.route("/")
def order_page():
    order_id = request.args.get("order_id")

    if not order_id:
        return render_template("order.html", order=None)

    order = get_selected_orders(order_id)

    # himoya: agar order topilmasa yoki noto‘g‘ri bo‘lsa
    try:
        order_data = order.get("order", [])
        if not order_data:
            order_data = None
        else:
            order_data = order_data[0]
    except Exception:
        order_data = None

    return render_template("order.html", order=order_data)


if __name__ == "__main__":
    app.run(debug=True)
