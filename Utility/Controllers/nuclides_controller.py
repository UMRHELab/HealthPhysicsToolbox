##### IMPORTS #####
import shelve
from Utility.Functions.files import get_user_data_path

#####################################################################################
# NUCLIDES UPDATE SECTION
#####################################################################################

"""
This function deletes the saved nuclides in the module.
"""
def delete_nuclides(module):
    db_path = get_user_data_path(f"Settings/{module}")
    with shelve.open(db_path) as prefs:
        if "nuclides" in prefs:
            del prefs["nuclides"]