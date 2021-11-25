from win32com.client import Dispatch


printer_com = Dispatch('Dymo.DymoAddIn')
print(printer_com.GetDymoPrinters())