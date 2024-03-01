from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableWidgetItem, QAction, QHeaderView
from PyQt5 import uic, QtGui
from qtpy.QtCore import Slot
import sys
from os.path import join, dirname, abspath
import qtmodern.styles
import qtmodern.windows
import NewProject
import OpenProject
import Db_Actions as DbAct
import info as info
import helpers as h
from printers import Dymo as dymo
from printers import Phomemo as phomemo
import asyncio
from bleak import BleakScanner
import webbrowser
from utils import *

_UI = join(dirname(abspath(__file__)), 'UI/PackerUI.ui')


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.widget = uic.loadUi(_UI, self)

        try:
            self.projectID, self.projectName = DbAct.get_current_project_id()
        except:
            self.projectID = None
            self.projectName = "None"

        window_title = self.projectName + info.app_name + info.version
        self.setWindowTitle(window_title)
        # Create new action
        newAction = QAction('&New', self)
        newAction.setShortcut('Ctrl+N')
        newAction.setStatusTip('New project')
        newAction.triggered.connect(self.new_project)

        # Open action
        openAction = QAction('&Open', self)
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Open project')
        openAction.triggered.connect(self.open_project)

        # Save Project action
        saveAction = QAction('&Save Settings', self)
        saveAction.setShortcut('Ctrl+S')
        saveAction.setStatusTip('Save Settings')
        # saveAction.triggered.connect(functools.partial(self.db_send_action, "save_settings"))

        # Printer Models
        self.printer_model = self.widget.printerModel
        self.printer_model.addItems(['Dymo450'])
        self.phomemo_printers = []

        # Scan Action
        self.lineedit = self.widget.cell_uuid
        self.lineedit.returnPressed.connect(self.add_cell_to_pack_pressed)

        self.lineedit_pack_creation = self.widget.cell_uuid_pack_creation
        self.lineedit_pack_creation.returnPressed.connect(self.find_cell_position)

        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        fileMenu.addAction(newAction)
        fileMenu.addAction(openAction)
        fileMenu.addAction(saveAction)

        table = self.widget.available_cells
        table.setHorizontalHeaderLabels(['UUID', 'Project', 'Capacity', 'Voltage', 'ESR', 'Added', 'Available',
                                         'Device'])

        self.widget.result_cells.setHorizontalHeaderLabels(['Cell', 'Capacity', 'CellsUUIDs'])

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.run())

        self.preview = QtGui.QPixmap(join(dirname(abspath(__file__)), "UI/deepcyclepower_banner.png"))
        self.widget.banner.setPixmap(self.preview)
        self.widget.banner.mousePressEvent = self.open_deepcycle_power

    @Slot()
    def on_load_all_cells_clicked(self):
        self.load_cells()

    @Slot()
    def on_add_cell_clicked(self):
        self.projectID, self.projectName = DbAct.get_current_project_id()
        voltage = self.validate_float(getattr(self.widget, "voltage").text())
        esr = self.validate_float(getattr(self.widget, "esr").text())
        capacity = self.validate_number(getattr(self.widget, "capacity").text())
        device = getattr(self.widget, "device").text()
        if voltage != "error" and esr != "error" and capacity != "error":
            DbAct.add_cell_to_db("Standard", self.projectID, voltage, capacity, esr, "Tested", device)
            self.load_cells()

    @Slot()
    def on_print_labels_clicked(self):
        table = self.widget.available_cells
        cells = []

        selected = table.selectedItems()
        rows = []
        if selected:
            for item in selected:
                if item.row() not in rows:
                    rows.append(item.row())

        for row in rows:
            uuid = table.item(row, 0).text()
            id = uuid.split("-")[1].replace("S", "")
            capacity = table.item(row, 2).text()
            voltage = table.item(row, 3).text()
            esr = table.item(row, 4).text()
            device = table.item(row, 7).text()
            cells.append({"uuid": uuid, "id": id, "capacity": capacity, "esr": esr, "voltage": voltage,
                          "device": device})

        if self.printer_model.currentText() == "Dymo450":
            dymo.print_label(cells)
        elif self.printer_model.currentText().startswith("Q119"):
            if len(self.phomemo_printers) > 0:
                printer_address = ""

                for d in self.phomemo_printers:
                    if d.name == self.printer_model.currentText():
                        printer_address = d.address

                if printer_address != "":
                    phomemo.print_label(cells, printer_address)
                else:
                    "Error : Printer Not found"

    @Slot()
    def on_add_cell_to_pack_clicked(self):
        self.add_cell_pressed_pack()

    @Slot()
    def on_remove_indexed_items_clicked(self):
        table = self.widget.indexed_cells
        self.delete_selected(table)
        print("Deleted Items")

    @Slot()
    def on_calculate_clicked(self):
        print("I got clicked")

        series = self.widget.series.text()
        parallel = self.widget.parallel.text()

        if series != "" and parallel != "":
            series = int(series)
            parallel = int(parallel)
        else:
            print("Please input valid numbers")
            return

        table = self.widget.indexed_cells
        cells = []
        for row in range(table.rowCount()):
            uuid = table.item(row, 0).text()
            id = uuid.split("-")[1].replace("S", "")
            capacity = table.item(row, 2).text()
            voltage = table.item(row, 3).text()
            esr = table.item(row, 4).text()
            device = table.item(row, 7).text()
            cells.append({"uuid": uuid, "id": id, "capacity": capacity, "esr": esr, "voltage": voltage,
                          "device": device})

        pack = h.calculate_pack(cells, series, parallel)
        self.add_pack_result(pack)

    @Slot()
    def on_load_debug_pressed(self):
        debug_list = ["D20211125-S000001-C3000", "D20211125-S000002-C3100", "D20211125-S000003-C3100", "D20211125-S00004-C2900", "D20211125-S00005-C2950", "D20211125-S00006-C2750", "D20211125-S00007-C2550", "D20211125-S00008-C2850", "D20211125-S00009-C2340", "D20211125-S00009-C2340", "D20211125-S00011-C2440", "D20211125-S00012-C2640", "D20220106-S00013-C2000"]
        for uuid in debug_list:
            cell_data = DbAct.get_gell_data(uuid)
            self.add_cell_to_pool(cell_data)


    def open_deepcycle_power(self, event):
        webbrowser.open('https://www.deepcyclepower.com/?utm_source=app&utm_medium=app&utm_campaign=packer1&utm_id=packerapp&utm_term=packer')

    def add_cell_to_pack_pressed(self):
        uuid = getattr(self.widget, "cell_uuid").text()
        cell_data = DbAct.get_gell_data(uuid)

        if cell_data is not None and cell_data != "NA":
            self.add_cell_to_pool(cell_data)
        elif cell_data is None:
            cell_data = uuid_decode(uuid)
            print(cell_data)
            if cell_data is not None:
                self.add_cell_to_pool(cell_data)
        else:
            print("Cell UUID is not Valid")

    def validate_number(self, number):
        try:
            number = int(number)
            return number
        except Exception:
            QMessageBox.about(self, 'Error', 'Input can only be a number')
            return "error"

    def validate_float(self, number):
        try:
            number = float(number)
            return number
        except Exception:
            QMessageBox.about(self, 'Error', 'Input can only be a number')
            return "error"

    def add_cell_to_pool(self, cell):
        table = self.widget.indexed_cells
        existing_uuids = []
        table.setHorizontalHeaderLabels(
            ['UUID', 'Project', 'Capacity', 'Voltage', 'ESR', 'Added', 'Available', 'Device'])

        nrows = table.rowCount()

        for row in range(0, nrows):
            uuid = table.item(row, 0).text()
            existing_uuids.append(uuid)

        if cell["UUID"] not in existing_uuids:
            i = 0
            table.insertRow(i)
            table.setItem(i, 0, QTableWidgetItem(cell["UUID"]))
            table.setItem(i, 1, QTableWidgetItem(cell["ProjectName"]))
            table.setItem(i, 2, QTableWidgetItem(str(cell["Capacity"])))
            table.setItem(i, 3, QTableWidgetItem(str(round(cell["Voltage"], 2))))
            table.setItem(i, 4, QTableWidgetItem(str(round(cell["ESR"], 2))))
            table.setItem(i, 5, QTableWidgetItem(str(cell["AddedDate"])))
            table.setItem(i, 6, QTableWidgetItem(cell["Available"]))
            table.setItem(i, 7, QTableWidgetItem(cell["Device"]))
            self.lineedit.clear()
            self.widget.info_box.setText(cell["UUID"] + " - Indexed")
        else:
            print("Cell already indexed")
            self.lineedit.clear()
            self.widget.info_box.setText(cell["UUID"] + " already indexed")

    def load_cells(self):
        total_cells = 0
        table = self.widget.available_cells
        table.clear()
        min_cap = int(self.widget.min_cap.text())
        max_cap = int(self.widget.max_cap.text())
        cells_info = DbAct.get_cells_info(min_cap, max_cap)
        cell_capacities = h.get_cells_capacity(cells_info)
        table.setHorizontalHeaderLabels(
            ['UUID', 'Project', 'Capacity', 'Voltage', 'ESR', 'Added', 'Available', 'Device'])

        table.setRowCount(0)

        for i, cell in enumerate(cells_info):
            table.insertRow(i)
            table.setItem(i, 0, QTableWidgetItem(str(cell["UUID"])))
            table.setItem(i, 1, QTableWidgetItem(str(cell["ProjectName"])))
            table.setItem(i, 2, QTableWidgetItem(str(round(cell["Capacity"], 2))))
            table.setItem(i, 3, QTableWidgetItem(str(round(cell["Voltage"], 2))))
            table.setItem(i, 4, QTableWidgetItem(str(round(cell["ESR"], 2))))
            table.setItem(i, 5, QTableWidgetItem(str(cell["AddedDate"])))
            table.setItem(i, 6, QTableWidgetItem(str(cell["Available"])))
            table.setItem(i, 7, QTableWidgetItem(str(cell["Device"])))
            total_cells += 1

        self.widget.total_loaded_cells.setText("Loaded: %s" % len(cells_info))
        self.widget.query_list_display_text.setPlainText(', '.join(str(x) for x in cell_capacities))

    def add_pack_result(self, pack):
        table = self.widget.result_cells
        table.clear()
        table.setRowCount(0)
        table.setHorizontalHeaderLabels(['Cell', 'Capacity', 'CellsUUIDs'])
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)

        i = 0
        for cell in pack:
            table.insertRow(i)
            table.setItem(i, 0, QTableWidgetItem(str(cell)))
            cell_uuids = []
            cell_capacity = 0
            for unit in pack[cell]:
                cell_uuids.append(unit["uuid"])
                cell_capacity += int(unit["capacity"])
            table.setItem(i, 1, QTableWidgetItem(str(cell_capacity)))
            table.setItem(i, 2, QTableWidgetItem(', '.join(cell_uuids)))


    def delete_selected(self, table):
        selected = table.selectedItems()
        rows = []
        if selected:
            for item in selected:
                if item.row() not in rows:
                    rows.append(item.row())

        print(rows)

        for row in reversed(rows):
            table.removeRow(row)

    def new_project(self):
        print("New project")
        newProjectWindow = qtmodern.windows.ModernWindow(NewProject.NewProject(mw))
        newProjectWindow.show()
        print(self.projectName)

    def open_project(self):
        print("opening project")
        openProjectWindow = qtmodern.windows.ModernWindow(OpenProject.OpenProject(mw))
        openProjectWindow.show()

    def find_cell_position(self):
        table = self.widget.result_cells
        cell_uuid = self.lineedit_pack_creation.text()
        found = False
        for row in range(table.rowCount()):
            uuids = (table.item(row, 2).text()).split(", ")
            remained_uuids = []
            for uuid in uuids:
                if uuid == cell_uuid:
                    cell_id = table.item(row, 0).text()
                    self.widget.position_in_pack.setText(cell_id)
                    found = True
                    self.lineedit_pack_creation.clear()
                    continue
                remained_uuids.append(uuid)

            table.setItem(row, 2, QTableWidgetItem(', '.join(remained_uuids)))

        if not found:
            self.widget.position_in_pack.setText("-")
            self.lineedit_pack_creation.clear()

    async def run(self):
        devices = await BleakScanner.discover()
        self.phomemo_printers = []
        for d in devices:
            if d.name.startswith("Q119"):
                self.phomemo_printers.append(d)
                print("Detected Printer %s, %s" % (d.name, d.address))
                self.printer_model.addItem(d.name)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    qtmodern.styles.dark(app)

    mw_class_instance = MainWindow()

    mw = qtmodern.windows.ModernWindow(mw_class_instance)

    mw.show()
    sys.exit(app.exec_())
