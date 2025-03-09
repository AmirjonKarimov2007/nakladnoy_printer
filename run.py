import requests
import json
import ssl
from requests.auth import HTTPBasicAuth

def get_info_for_product():
    url = "https://smartup.online/b/trade/txs/tdeal/order$export"


    auth = HTTPBasicAuth('jamshidbek@falcon', '571++632')

    headers = {
        'filial_id': '5012602',
        'project_id': 'trade',
        'Content-Type': 'application/json'
    }

    data = {
        "filial_codes": [
            {
            "filial_code": ""
            }
        ],
        "statuses":[""],
        "filial_code": "",
        "external_id": "",
        "deal_id": "",
        "begin_deal_date": "",
        "end_deal_date": "",
        "delivery_date": "",
        "begin_created_on": "",
        "end_created_on": "",
        "begin_modified_on": "",
        "end_modified_on": ""
        }

    response = requests.get(url, json=data, auth=auth, headers=headers)

    if response.status_code == 200:
        
        # JSON ma'lumotlarini dekodlash
        response_dict = response.json()

        # Ma'lumotlarni tartibli JSON faylga yozish va Unicode belgilarni to'g'ri ko'rsatish
        with open('today_orders.json', 'w', encoding='utf-8') as file:
            json.dump(response_dict, file, indent=4, ensure_ascii=False)
        return True
    else:

        return False
    
get_info_for_product()