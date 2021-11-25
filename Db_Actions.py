import sql as Connection
import helpers as h
from sqlalchemy.sql import func
from datetime import date

def reset_to_no_project():
    Session = Connection.sessionmaker(bind=Connection.engine)
    sqlSession = Session()
    other_settings_query = sqlSession.query(Connection.OtherSettings).filter_by(ID=1).first()
    if other_settings_query is not None:
        other_settings_query.CurrentProjectID = -1
        sqlSession.commit()

    sqlSession.close()


def generate_uuid(capacity):
    Session = Connection.sessionmaker(bind=Connection.engine)
    sqlSession = Session()
    other_settings_query = sqlSession.query(Connection.OtherSettings).filter_by(ID=1).first()
    uuids = []

    if other_settings_query is not None:
        if other_settings_query.CurrentProjectID != -1:
            proj_id = other_settings_query.CurrentProjectID
            project_query = sqlSession.query(Connection.Projects).filter_by(ID=proj_id).first()
            if project_query is not None:
                project_name = project_query.Name
                if project_query.LastCellNumber is None:
                    # project_query.LastCellNumber = 16
                    last_cell_id = 0
                    sqlSession.commit()

                else:
                    last_cell_id = project_query.LastCellNumber
                    project_query.LastCellNumber += 1
                    sqlSession.commit()

                today = str(date.today())
                today = today.replace("-", "")
                print("Today's date:", today )
                uuid = "D" + today + "-S" + str(last_cell_id + 1).zfill(5) + "-C" + str(capacity)
                return uuid
        else:
            # h.showdialog("No project set", "Create new or open existing project")
            return []

        sqlSession.close()
    else:
        return []


def get_current_project_id():
    Session = Connection.sessionmaker(bind=Connection.engine)
    sqlSession = Session()
    other_settings_query = sqlSession.query(Connection.OtherSettings).filter_by(ID=1).first()
    project_id = other_settings_query.CurrentProjectID

    project_query = sqlSession.query(Connection.Projects).filter_by(ID=project_id).first()

    project_name = project_query.Name
    if project_id == -1:
        h.showdialog("No project set", "Create new or open existing project")
        sqlSession.close()
        return None

    sqlSession.close()
    return project_id, project_name


def get_cells_info(min, max):
    project_id, project_name = get_current_project_id()
    print(project_id)
    cells_info = []
    if project_id:
        Session = Connection.sessionmaker(bind=Connection.engine)
        sqlSession = Session()
        cells_query = sqlSession.query(Connection.Cells).filter_by(ProjectID=project_id)


        cells_info = []

        if cells_query is None:
            sqlSession.close()
            return []
        project_query = sqlSession.query(Connection.Projects).filter_by(ID=project_id).first()

        for cell in cells_query:
            if (cell.Capacity >= min and cell.Capacity <= max) and cell.Available == "YES":
                cell_data = dict()
                cell_data["ProjectID"] = project_id
                cell_data["ID"] = cell.ID
                cell_data["ProjectName"] = project_query.Name
                cell_data["UUID"] = cell.UUID
                cell_data["Voltage"] = cell.Voltage
                cell_data["Capacity"] = cell.Capacity
                cell_data["ESR"] = cell.ESR
                cell_data["CellType"] = cell.CellType
                cell_data["AddedDate"] = cell.AddedDate.strftime("%Y-%m-%d %H:%M:%S")
                cell_data["Available"] = cell.Available
                cell_data["Device"] = cell.Device
                cells_info.append(cell_data)

        sqlSession.close()
    return cells_info


def get_cell_by_capacity(capacity, already_added):
    project_id = get_current_project_id()
    Session = Connection.sessionmaker(bind=Connection.engine)
    sqlSession = Session()
    cells_query = sqlSession.query(Connection.Cells).filter_by(ProjectID=project_id, Capacity=capacity).first()

    if cells_query is not None:
        return cells_query.UUID
    else:
        return None
    #
    # for cell in cells_query:
    #     print("Got in here")
    #     print(cell.UUID)
    #     if cell.UUID not in already_added:
    #         return cell.UUID
    # return None


def add_cell_to_db(celltype, projectID, voltage, capacity, esr, status, device):
    Session = Connection.sessionmaker(bind=Connection.engine)
    sqlSession = Session()
    uuid = generate_uuid(capacity)
    print(uuid)

    cell_register = Connection.Cells(ProjectID=projectID, Voltage=voltage, Capacity=int(capacity),
                                     ESR=esr, AddedDate=func.current_timestamp(), UUID=uuid,
                                     Available="YES", CellType=celltype, Status=status, Device=device)


    sqlSession.merge(cell_register)
    sqlSession.commit()
    sqlSession.close()


def mark_cells_used(uuids):
    Session = Connection.sessionmaker(bind=Connection.engine)
    sqlSession = Session()

    for uuid in uuids:
        cell = sqlSession.query(Connection.Cells).filter_by(UUID=uuid).first()
        if cell is not None:
            cell.Available = "NO"
            sqlSession.commit()
    sqlSession.close()


def get_gell_data(uuid):
    project_id, project_name = get_current_project_id()
    print(project_id)
    cells_info = []

    if project_id:
        Session = Connection.sessionmaker(bind=Connection.engine)
        sqlSession = Session()
        cell = sqlSession.query(Connection.Cells).filter_by(UUID=uuid).first()
        project_query = sqlSession.query(Connection.Projects).filter_by(ID=project_id).first()
        if cell is not None:
            if cell.Available == "YES":
                cell_data = dict()
                cell_data["ProjectID"] = project_id
                cell_data["ID"] = cell.ID
                cell_data["ProjectName"] = project_query.Name
                cell_data["UUID"] = cell.UUID
                cell_data["Voltage"] = cell.Voltage
                cell_data["Capacity"] = cell.Capacity
                cell_data["ESR"] = cell.ESR
                cell_data["CellType"] = cell.CellType
                cell_data["AddedDate"] = cell.AddedDate.strftime("%Y-%m-%d %H:%M:%S")
                cell_data["Available"] = cell.Available
                cell_data["Device"] = cell.Device
                cells_info.append(cell_data)

                return cell_data
            else:
                return "Cell In Use"

        else:
            return "None"

    else:
        return "None"