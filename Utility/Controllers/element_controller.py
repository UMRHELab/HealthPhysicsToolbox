##### IMPORTS #####
import shelve
from Utility.Functions.files import get_user_data_path

#####################################################################################
# CONTROLLER SECTION
#####################################################################################

"""
This function causes an update of elements due to a change in element.
"""
def update_elements(category, module, value):
    # Gets common_el and element from user prefs
    db_path = get_user_data_path(f"Settings/{module}")
    with shelve.open(db_path) as prefs:
        common_el = prefs.get("common_el", "Ag")
        element = prefs.get("element", "Ac")

    new_element = element
    new_common_el = common_el

    if category == "All Elements":
        new_element = value
        with shelve.open(db_path) as shelve_prefs:
            shelve_prefs["element"] = value
    else:
        new_common_el = value
        with shelve.open(db_path) as shelve_prefs:
            shelve_prefs["common_el"] = value

    return new_common_el, new_element