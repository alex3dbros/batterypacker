from os.path import join, dirname, abspath
from qtpy import uic
from qtpy.QtCore import Slot, QTimer
from qtpy.QtWidgets import QApplication, QMainWindow, QMessageBox, QAction, QDialog, qApp
import sql as Connection
from sqlalchemy.sql import func
import Db_Actions as DbAct
import info as info

new_project_UI = join(dirname(abspath(__file__)), 'NewProject.ui')


class NewProject(QDialog):
    def __init__(self, main_window):
        QDialog.__init__(self)

        self.widget = uic.loadUi(new_project_UI, self)
        self.mw_ref = main_window
        print("got class instance")


    @Slot()
    def on_pushButton_clicked(self):
        self.close()
        self.widget.new_proj_label.setText("Enter New Project Name")
        self.widget.new_proj_label.setStyleSheet('')

    @Slot()
    def on_cancel_clicked(self):
        self.close()
        self.widget.new_proj_label.setText("Enter New Project Name")
        self.widget.new_proj_label.setStyleSheet('')
        print("Got close event 2")

    @Slot()
    def closeEvent(self, event):
        print("Got close event")
        event.accept()


    @Slot()
    def on_create_clicked(self):
        Session = Connection.sessionmaker(bind=Connection.engine)
        sqlSession = Session()

        new_project_name = self.widget.project_name.text()

        project_query = sqlSession.query(Connection.Projects).filter_by(Name=new_project_name).first()

        if project_query is not None:
            self.widget.new_proj_label.setText("Project Already Exists!")
            self.widget.new_proj_label.setStyleSheet('color: red')

        if project_query is None:
            project_register = Connection.Projects(Name=new_project_name, LastCellNumber=0, CreationDate=func.current_timestamp())
            sqlSession.merge(project_register)
            sqlSession.commit()

            other_settings_query = sqlSession.query(Connection.OtherSettings).filter_by(ID=1).first()
            project_query2 = sqlSession.query(Connection.Projects).filter_by(Name=new_project_name).first()

            if other_settings_query is None:
                setting_register = Connection.OtherSettings(CurrentProjectID=project_query2.ID)
                sqlSession.merge(setting_register)
                sqlSession.commit()
            else:
                other_settings_query.CurrentProjectID = project_query2.ID
                sqlSession.commit()

            # self.widget.new_proj_label.setText("Enter New Project Name")
            # self.widget.new_proj_label.setStyleSheet('')

            window_title = new_project_name + info.app_name + info.version
            self.mw_ref.setWindowTitle(window_title)

            print("got here now1")

            # uuids = DbAct.generate_uuid(1)
            # if len(uuids) > 0:
            #     print("got here now2")
            #     self.mw_class.update_ui_uuids(uuids)
            print("got here now3")
            # if len(uuids) > 0:
            #     Action.update_ui_uuids(self.mw_class.widget, 16, uuids)

            # self.close()

        sqlSession.close()