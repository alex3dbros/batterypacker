import json
from qtpy.QtWidgets import QMessageBox
import sql as Connection


def secondsToText(secs):
    days = secs//86400
    hours = (secs - days*86400)//3600
    minutes = (secs - days*86400 - hours*3600)//60
    seconds = secs - days*86400 - hours*3600 - minutes*60
    result = ("{} da, ".format(days) if days else "") + \
    ("{} h, ".format(hours) if hours else "") + \
    ("{} m, ".format(minutes) if minutes else "") + \
    ("{} s ".format(seconds) if seconds else "")
    return result


def showdialog(window_title, message):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)

    msg.setText(message)
    # msg.setInformativeText("This is additional information")
    msg.setWindowTitle(window_title)
    # msg.setDetailedText("The details are as follows:")
    msg.setStandardButtons(QMessageBox.Ok)
    # msg.buttonClicked.connect(msgbtn)
    msg.exec_()


def get_cells_capacity(capacities_dict):
    cap_list = []
    for cell in capacities_dict:
        cap_list.append(round(cell["Capacity"], 2))

    return cap_list

