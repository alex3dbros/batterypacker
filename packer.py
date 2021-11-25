from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QDialog, QTableWidgetItem, QAction
from PyQt5 import uic
from qtpy.QtCore import Slot, QTimer
import sys
from os.path import join, dirname, abspath
import qtmodern.styles
import qtmodern.windows
import NewProject
import OpenProject
import Db_Actions as DbAct
import info as info
import helpers as h
import printlabel_dymo as dymo

_UI = join(dirname(abspath(__file__)), 'PackerUI.ui')


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

        # Scan Action
        self.lineedit = self.widget.cell_uuid
        self.lineedit.returnPressed.connect(self.add_cell_pack_pressed)

        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        fileMenu.addAction(newAction)
        fileMenu.addAction(openAction)
        fileMenu.addAction(saveAction)

        table = self.widget.available_cells
        table.setHorizontalHeaderLabels(['UUID', 'Project', 'Capacity', 'Voltage', 'ESR', 'Added', 'Available',
                                         'Device'])


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
        dymo.print_label(cells)


    @Slot()
    def on_add_cell_pack_clicked(self):
        self.add_cell_pressed_pack()

    @Slot()
    def on_remove_indexed_items_clicked(self):
        table = self.widget.indexed_cells
        self.delete_selected(table)
        print("Deleted Items")

    def add_cell_pack_pressed(self):
        uuid = getattr(self.widget, "cell_uuid").text()
        cell_data = DbAct.get_gell_data(uuid)
        print(cell_data)
        self.add_cell_to_pack(cell_data)


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

    def add_cell_to_pack(self, cell):
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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    qtmodern.styles.dark(app)

    mw_class_instance = MainWindow()

    mw = qtmodern.windows.ModernWindow(mw_class_instance)


    mw.show()
    sys.exit(app.exec_())
