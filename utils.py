import Db_Actions as DbAct
from datetime import datetime
import re
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

    pattern = r'-C(\d+)'

    match = re.search(pattern, uuid)
    if match:
        capacity = match.group(1)
    else:
        capacity = 0

    project_id, project_name = DbAct.get_current_project_id()


    cell_data = dict()
    cell_data["ProjectID"] = project_id
    cell_data["ProjectName"] = "Unknown"
    cell_data["UUID"] = uuid
    cell_data["Voltage"] = 3.7
    cell_data["Capacity"] = capacity
    cell_data["ESR"] = 0
    cell_data["CellType"] = "Unknown"
    cell_data["Available"] = "YES"
    cell_data["Device"] = "Unknown"

    date_pattern = r'D(\d{8})'

    match = re.search(date_pattern, uuid)

    if match:
        # Extracted date string
        date_str = match.group(1)
        # Parse the extracted date string into a datetime object
        parsed_date = datetime.strptime(date_str, "%Y%m%d")
        # Create the cell_data dictionary and add the "AddedDate" key with the formatted date
        cell_data["AddedDate"] = parsed_date.strftime("%Y-%m-%d %H:%M:%S")
    else:
        cell_data["AddedDate"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return cell_data