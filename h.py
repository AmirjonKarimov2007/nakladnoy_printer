import win32print

def set_default_printer(printer_name="Canon MF3010"):
    try:
        win32print.SetDefaultPrinter(printer_name)
        print(f"Default printer set to: {printer_name}")
    except Exception as e:
        print(f"Error: {e}")