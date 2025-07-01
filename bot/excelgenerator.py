import os
import asyncio
from openpyxl import load_workbook
from openpyxl.styles import PatternFill, Alignment, Border, Side, Font
from openpyxl.utils import get_column_letter
import os
from functions import *
import pythoncom
import psutil
import os
import asyncio
import psutil
import pythoncom
from data.config import USD
from loader import db


def kill_task():
    task_name = 'EXCEL.EXE'
    for proc in psutil.process_iter(['pid', 'name']):
        if task_name.lower() in proc.info['name'].lower(): 
            try:
                proc.kill()  
            except psutil.NoSuchProcess:
                pass
            except psutil.AccessDenied:
                pass



import httpx
import asyncio
async def send_print_request(payload: dict, url: str = "https://myprinter123.loca.lt/print"):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload)
            print("✅ Status:", response.status_code)
            print("📨 Response:", response.json())
            return response
        except httpx.HTTPError as e:
            print("❌ HTTP xatolik:", e)
            return None


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
def format_barcode(barcode):
    barcode = str(barcode)
    if '|' in barcode:
        return barcode.replace('|', '\n')
    return barcode
def format_product_name(name, max_length=45):
    formatted_name = ' '.join(name.split())
    if len(formatted_name) > max_length:
        formatted_name = '\n'.join([formatted_name[i:i+max_length] for i in range(0, len(formatted_name), max_length)])
    return formatted_name
def set_column_width(ws, col_idx, start_row, end_row):
    max_length = 0
    for row in range(start_row, end_row + 1):
        cell = ws.cell(row=row, column=col_idx)
        try:
            if len(str(cell.value)) > max_length:
                max_length = len(str(cell.value))
        except:
            pass
    adjusted_width = (max_length + 2)
    ws.column_dimensions[get_column_letter(col_idx)].width = adjusted_width
async def process_order(deal_id, output_path, moment,moneytype = "usd"):
    try:
        if moment == 'today':
            order_info = await get_today_order_info_by_deal_id(deal_id)
        elif moment == 'yesterday':
            order_info = await get_lastday_order_info_by_deal_id(deal_id)
        else:
            order_info = await get_order_info_by_deal_id(deal_id)
        process = await send_print_request(payload=order_info)
        
        if process:
            return True
        else:
            return False
        
    except Exception as e:
        if "Permission denied" in str(e):
            kill_task()
            return True
        else:
            print(f"Xatolik yuz beribdi: {e}")
            return False
async def main():
    await process_order(deal_id="120462256",output_path="1",moment='today')
def update_excel_with_products(file_path: str, products_data: list, output_path: str = "tahrirlangan_rasxod.xlsx"):
    wb = load_workbook(file_path)
    ws = wb.active
    start_row = 2
    for index, product in enumerate(products_data, start=start_row):
        ws.cell(row=index, column=1, value=product.get("product_code", ""))
        ws.cell(row=index, column=2, value=product.get("order_quant", 0))
        ws.cell(row=index, column=3, value="Y")
    wb.save(output_path)
    return output_path