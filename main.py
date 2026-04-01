from flask import Flask, render_template, request, jsonify, Response
import requests
import json
import pytz
from datetime import datetime

# =========================
# CONFIG
# =========================
SMARTUP_URL = "https://smartup.online/b/trade/txs/tdeal/order$export"
INVENTORY_URL = "https://smartup.online/b/anor/mxsx/mr/inventory$export"
SMARTUP_AUTH = ('ramazon14@falcon', '111222')   # KEYIN .env GA O'TKAZING
FILIAL_ID = '5012602'
PROJECT_CODE = 'trade'
PROJECT_ID = 'trade'

uzbekistan_tz = pytz.timezone('Asia/Tashkent')
today = datetime.now(uzbekistan_tz).strftime('%d.%m.%Y')

app = Flask(__name__, template_folder="templates", static_folder="static")


# =========================
# HELPERS
# =========================
def safe_float(v):
    try:
        return float(v or 0)
    except Exception:
        return 0.0


def safe_str(v):
    return str(v or "").strip()


def build_image_url(product_id):
    # Sizning GitHub image bazangiz
    return f"https://media.githubusercontent.com/media/AmirjonKarimov2007/rasmlar/main/{product_id}.jpg"


def get_selected_orders(deal_id: str):
    headers = {
        'filial_id': FILIAL_ID,
        'project_code': PROJECT_CODE,
    }

    data = {
        "filial_codes": [{"filial_code": FILIAL_ID}],
        "deal_id": deal_id,
        "statuses": [],
        "begin_deal_date": "",
        "end_deal_date": "",
    }

    try:
        response = requests.post(
            SMARTUP_URL,
            json=data,
            headers=headers,
            auth=SMARTUP_AUTH,
            verify=False,
            timeout=30
        )

        if response.status_code != 200:
            print(f"❌ API status code: {response.status_code}")
            return None

        try:
            return response.json()
        except json.JSONDecodeError:
            print("❌ JSON parse error")
            return None

    except Exception as e:
        print(f"❌ API bilan muammo: {e}")
        return None


def normalize_order(order_data):
    if not order_data:
        return None

    products = []
    raw_products = order_data.get("order_products", []) or []

    total_qty = 0
    total_amount = 0

    # products.json'dan box_quant olish
    products_json_data = load_products_json()

    for i, p in enumerate(raw_products, start=1):
        qty = safe_float(p.get("sold_quant"))
        price = safe_float(p.get("product_price"))
        amount = safe_float(p.get("sold_amount"))

        total_qty += qty
        total_amount += amount

        # box_quent topish
        box_quant = 0
        product_id = safe_str(p.get("product_id"))
        barcode = safe_str(p.get("product_barcode"))

        if products_json_data:
            # products.json dan qidirish
            products_array = products_json_data.get("inventory", []) if isinstance(products_json_data, dict) else products_json_data
            for prod in products_array:
                if (safe_str(prod.get("product_id")) == product_id or
                    safe_str(prod.get("barcodes")) == barcode or
                    safe_str(prod.get("code")) == barcode):
                    box_quant = safe_float(prod.get("box_quant")) or 0
                    break

        products.append({
            "index": i,
            "product_id": product_id,
            "barcode": barcode,
            "name": safe_str(p.get("product_name")),
            "qty": qty,
            "price": price,
            "total": amount,
            "box_quant": box_quant,
            "image_url": build_image_url(product_id)
        })

    return {
        "deal_id": safe_str(order_data.get("deal_id")),
        "filial_code": safe_str(order_data.get("filial_code")),
        "deal_time": safe_str(order_data.get("deal_time")),
        "items_count": len(products),
        "total_qty": total_qty,
        "total_amount": total_amount,
        "products": products
    }


# =========================
# ROUTES
# =========================
@app.route("/")
def home():
    order_id = request.args.get("order_id", "").strip()

    if not order_id:
        return render_template("index.html", today=today)

    # MANUAL_ bilan boshlangan orderlar API'dan emas, localStorage'dan olinadi
    if order_id.startswith("MANUAL_"):
        # order.html'da JavaScript localStorage'dan ma'lumotni olib ishlaydi
        return render_template("order.html", order=None, today=today, is_manual_order=True)

    raw = get_selected_orders(order_id)

    try:
        order_list = raw.get("order", [])
        if not order_list:
            return render_template("order.html", order=None, today=today)

        order = normalize_order(order_list[0])
    except Exception:
        order = None

    return render_template("order.html", order=order, today=today)


@app.route("/api/order")
def api_order():
    order_id = request.args.get("order_id", "").strip()

    if not order_id:
        return jsonify({"ok": False, "message": "order_id kiritilmadi"}), 400

    raw = get_selected_orders(order_id)

    try:
        order_list = raw.get("order", [])
        if not order_list:
            return jsonify({"ok": False, "message": "Buyurtma topilmadi"}), 404

        order = normalize_order(order_list[0])
        return jsonify({"ok": True, "order": order})
    except Exception:
        return jsonify({"ok": False, "message": "Ma'lumotni qayta ishlashda xatolik"}), 500


# =========================
# INVENTORY API
# =========================
def get_inventory_data(code="", begin_created_on="", end_created_on="", begin_modified_on="", end_modified_on=""):
    headers = {
        'filial_id': FILIAL_ID,
        'project_id': PROJECT_ID,
        'Content-Type': 'application/json'
    }

    data = {
        "code": code,
        "begin_created_on": begin_created_on,
        "end_created_on": end_created_on,
        "begin_modified_on": begin_modified_on,
        "end_modified_on": end_modified_on
    }

    try:
        response = requests.get(
            INVENTORY_URL,
            json=data,
            headers=headers,
            auth=SMARTUP_AUTH,
            verify=False,
            timeout=30
        )

        if response.status_code != 200:
            print(f"❌ Inventory API status code: {response.status_code}")
            return None
# yangi git uchun
        try:
            return response.json()
        except Exception:
            print("❌ Inventory JSON parse error")
            return None

    except Exception as e:
        print(f"❌ Inventory API bilan muammo: {e}")
        return None


def load_products_json():
    """products.json fayldan ma'lumot olish"""
    try:
        with open('products.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"❌ products.json o'qishda xatolik: {e}")
        return None


def save_to_products_json(data):
    try:
        with open('products.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        print("✅ products.json ga saqlandi")
        return True
    except Exception as e:
        print(f"❌ products.json ga saqlashda xatolik: {e}")
        return False


@app.route("/api/update-products")
def update_products():
    try:
        inventory_data = get_inventory_data()

        if not inventory_data:
            return jsonify({"ok": False, "message": "Ma'lumot olishda xatolik"}), 500

        success = save_to_products_json(inventory_data)

        if success:
            return jsonify({"ok": True, "message": "Mahsulotlar yangilandi"})
        else:
            return jsonify({"ok": False, "message": "Ma'lumot saqlashda xatolik"}), 500

    except Exception as e:
        print(f"❌ Update products error: {e}")
        return jsonify({"ok": False, "message": "Xatolik yuz berdi"}), 500


@app.route("/products.json")
def serve_products_json():
    """Frontend uchun products.json endpoint"""
    try:
        with open('products.json', 'r', encoding='utf-8') as f:
            content = f.read()
        return Response(content, mimetype='application/json', headers={'Content-Type': 'application/json; charset=utf-8'})
    except FileNotFoundError:
        return jsonify({"error": "products.json topilmadi. Avval 'Mahsulotlarni yangilash' tugmasini bosing"}), 404
    except Exception as e:
        print(f"❌ products.json o'qishda xatolik: {e}")
        return jsonify({"error": "Xatolik yuz berdi"}), 500


if __name__ == "__main__":
    app.run(debug=True)