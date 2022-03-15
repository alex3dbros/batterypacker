import Db_Actions as DbAct
from datetime import datetime

def validate_uuid(uuid):
    if uuid.startswith("D") and "-" in uuid:
        return True
    else:
        return False


def uuid_decode(uuid):
    # We don't have info about this cell, but we import it to be used for pack creation

    # Check if it's a valid serial number
    if not validate_uuid(uuid):
        return None

    capacity = uuid.split("-")[-1]
    capacity = capacity.replace("C", "")

    project_id, project_name = DbAct.get_current_project_id()

    cell_data = dict()
    cell_data["ProjectID"] = project_id
    cell_data["ProjectName"] = "Unknown"
    cell_data["UUID"] = uuid
    cell_data["Voltage"] = 3.7
    cell_data["Capacity"] = capacity
    cell_data["ESR"] = 0.1
    cell_data["CellType"] = "Unknown"
    cell_data["AddedDate"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cell_data["Available"] = "YES"
    cell_data["Device"] = "Unknown"
    return cell_data