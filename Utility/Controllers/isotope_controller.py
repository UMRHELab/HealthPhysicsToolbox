##### IMPORTS #####
import shelve
from Utility.Functions.choices import get_isotopes
from Utility.Functions.gui_utility import get_width
from Utility.Functions.files import get_user_data_path
from Utility.Controllers.nuclides_controller import delete_nuclides

#####################################################################################
# CONTROLLER SECTION
#####################################################################################

"""
This function causes a full update of isotopes due to a change in category or element.
"""
def update_isotopes(category, module, new_element, compare_element, var_isotope,
                    isotope_dropdown, tracking_nuclides = False):
    isotopes = get_isotopes(new_element)
    isotope = None

    # Gets common_el, element, isotope from user prefs
    db_path = get_user_data_path(f"Settings/{module}")
    with shelve.open(db_path) as prefs:
        common_el = prefs.get("common_el", "Ag")
        element = prefs.get("element", "Ac")
        isotope = prefs.get("isotope", isotopes[0] if isotopes else "")

    if category == "Common Elements":
        if common_el != compare_element:
            isotope = isotopes[0] if isotopes else ""
            if tracking_nuclides:
                delete_nuclides(module)
            with shelve.open(db_path) as prefs:
                prefs["isotope"] = isotope
    else: # category == "All Elements"
        if element != compare_element:
            isotope = isotopes[0] if isotopes else ""
            if tracking_nuclides:
                delete_nuclides(module)
            with shelve.open(db_path) as prefs:
                prefs["isotope"] = isotope

    var_isotope.set(isotope)
    isotope_dropdown.config(values=isotopes, width=get_width(isotopes))
    return isotope