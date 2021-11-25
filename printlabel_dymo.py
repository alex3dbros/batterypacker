import sys
from os import path
from win32com.client import Dispatch
from tkinter import Tk
import tkinter.messagebox as mbox

curdir = None
if getattr(sys, 'frozen', False):
    # frozen
    curdir = path.dirname(sys.executable)
else:
    # unfrozen
    curdir = path.dirname(path.abspath(__file__))

mylabel = path.join(curdir, 'labeltemplates\Dymo\qr-11353.label')
window = Tk()
window.wm_withdraw()

if not path.isfile(mylabel):
    mbox.showinfo('PyDymoLabel', 'Template file does not exist')
    sys.exit(1)


def print_label(cells):

    if len(cells) % 2 != 0:
        cells.append(cells[-1])

    batch_size = 2
    if len(cells) > 1:
        for i in range(0, len(cells)-batch_size+1, batch_size):
            batch = cells[i:i+batch_size]
            print("Batch: ", batch)

            if len(batch) == 2:
                cap1_string = batch[0]["id"] + "-C:" + str(batch[0]["capacity"])
                etvm1_string = "E:" + str(batch[0]["esr"]) + "\n" + "V:" + str(batch[0]["voltage"]) + "\n" + batch[0][
                    "device"]

                cap2_string = batch[1]["id"] + "-C:" + str(batch[1]["capacity"])
                etvm2_string = "E:" + str(batch[1]["esr"]) + "\n" + "V:" + str(batch[1]["voltage"]) + "\n" + batch[1][
                    "device"]

                try:
                    labelCom = Dispatch('Dymo.DymoAddIn')
                    labelText = Dispatch('Dymo.DymoLabels')
                    labelCom.Open(mylabel)
                    selectPrinter = 'DYMO LabelWriter 450'
                    labelCom.SelectPrinter(selectPrinter)

                    labelText.SetField('CAPACITY', cap1_string)
                    labelText.SetField('ETVM', etvm1_string)
                    labelText.SetField('BARCODE', batch[0]["uuid"])

                    labelText.SetField('CAPACITY_1', cap2_string)
                    labelText.SetField('ETVM_1', etvm2_string)
                    labelText.SetField('BARCODE_1', batch[1]["uuid"])


                    labelCom.StartPrintJob()
                    labelCom.Print(1, False)
                    labelCom.EndPrintJob()
                except:
                    mbox.showinfo('PyDymoLabel', 'An error occurred during printing.')
                    sys.exit(1)


