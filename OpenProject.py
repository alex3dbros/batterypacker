from os.path import join, dirname, abspath
from qtpy import uic
from qtpy.QtCore import Slot, QTimer
from qtpy.QtWidgets import QApplication, QMainWindow, QMessageBox, QAction, QDialog
import sql as Connection
import Db_Actions as DbAct
import info as info
open_project_UI = join(dirname(abspath(__file__)), 'OpenProject.ui')


class OpenProject(QDialog):
    def __init__(self, main_window):
        QDialog.__init__(self)

        self.widget = uic.loadUi(open_project_UI, self)
        self.load_projects()
        self.mw_ref = main_window
        print("Class initialized again")

    def load_projects(self):

        Session = Connection.sessionmaker(bind=Connection.engine)
        sqlSession = Session()

        project_query = sqlSession.query(Connection.Projects).all()
        if project_query is not None:
            project_names = [name.Name for name in project_query]
            if len(project_names) == 0:
                self.widget.open.setEnabled(False)
            else:
                self.widget.open.setEnabled(True)

            self.widget.project_combo.clear()
            self.widget.project_combo.addItems(project_names)


        sqlSession.close()

    @Slot()
    def on_pushButton_clicked(self):
        self.close()

    @Slot()
    def on_refresh_button_clicked(self):
        self.load_projects()

    @Slot()
    def on_cancel_clicked(self):
        self.close()

    @Slot()
    def closeEvent(self, event):
        event.accept()


    @Slot()
    def on_open_clicked(self):
        Session = Connection.sessionmaker(bind=Connection.engine)
        sqlSession = Session()
        print("I am here1")
        project_name = self.widget.project_combo.currentText()
        print(project_name)
        window_title = project_name + info.app_name + info.version
        print(window_title)
        self.mw_ref.setWindowTitle(window_title)

        other_settings_query = sqlSession.query(Connection.OtherSettings).filter_by(ID=1).first()
        project_query = sqlSession.query(Connection.Projects).filter_by(Name=project_name).first()
        print("I am here2")
        if other_settings_query is None:
            setting_register = Connection.OtherSettings(CurrentProjectID=project_query.ID)
            sqlSession.merge(setting_register)
            sqlSession.commit()
        else:
            other_settings_query.CurrentProjectID = project_query.ID
            sqlSession.commit()
        print("I am here3")
        # uuids = DbAct.generate_uuid(16, self.mw_class.connect_to)
        #self.mw_class.update_ui_uuids(uuids)

        #self.close()

