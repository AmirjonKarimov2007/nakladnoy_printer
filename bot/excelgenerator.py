import win32com.client
import os
import asyncio
from openpyxl import load_workbook
from openpyxl.styles import PatternFill, Alignment, Border, Side, Font
from openpyxl.utils import get_column_letter
import os
import win32com.client
from functions import *
import pythoncom
import psutil
import os
import asyncio
import psutil
import pythoncom
import win32com.client
from data.config import USD
from loader import db
import win32print

def set_default_printer(printer_name="Canon MF3010"):
    try:
        win32print.SetDefaultPrinter(printer_name)
        print(f"Default printer set to: {printer_name}")
    except Exception as e:
        print(f"Error: {e}")
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
def print_excel_file_sync(file_path):
    try:
        set_default_printer()
        pythoncom.CoInitialize()
        abs_path = os.path.abspath(file_path)  
        excel = win32com.client.Dispatch("Excel.Application")
        excel.Visible = False 
        wb = excel.Workbooks.Open(abs_path)  
        ws = wb.ActiveSheet

        # Chop etish sozlamalari
        ws.PageSetup.Zoom = False
        ws.PageSetup.FitToPagesWide = 1
        ws.PageSetup.FitToPagesTall = False 
        ws.PageSetup.PaperSize = 9  # A4 qog'oz o'lchami
        ws.PageSetup.Orientation = 1  # Portret rejimi

        # Chop etish (faqat qora-oq rejimda)
        # ws.PageSetup.PrintInBlackAndWhite = True  # <-- Qora-oq rejim
        wb.PrintOut()
        
        # Faylni yopish va Excel ilovasini to'xtatish
        wb.Close(SaveChanges=False)
        excel.Quit()
        pythoncom.CoUninitialize()
        return True
    except Exception as e:
        print(f"Xatolik yuz berdi: {e}")
        return False 
    finally:
        kill_task()

async def print_excel_file(file_path):
    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, print_excel_file_sync, file_path)
        if result:
            return True
        else:
            return False
    except Exception as e:
        print(f"Asinxron xatolik yuz berdi: {e}")
        return False

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