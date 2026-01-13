##### IMPORTS #####
import shelve
import radioactivedecay as rd
from Utility.Functions.files import get_user_data_path
from Utility.Functions.gui_utility import edit_result, no_selection
from Utility.Functions.math_utility import atomic_mass_numerator, atomic_mass_denominator

#####################################################################################
# CALCULATIONS SECTION
#####################################################################################

"""
This function is called when the Calculate button is hit.
The function handles the following error:
   No selected element
The function decides what calculation to perform
based on the selected calculation mode.
"""
def handle_calculation(root, mode, isotope, result_box):
    root.focus()

    # Error-check for no selected element
    if isotope == "":
        edit_result(no_selection, result_box)
        return

    match mode:
        case "Proton Number":
            nuclide_proton_number(isotope, result_box)
        case "Nucleon Number":
            nuclide_nucleon_number(isotope, result_box)
        case "Atomic Mass":
            nuclide_atomic_mass(isotope, result_box)

"""
This function retrieves the proton number
given a particular isotope.
"""
def nuclide_proton_number(isotope, result_box):
    nuc = rd.Nuclide(isotope)
    result = nuc.Z
    edit_result(result, result_box)

"""
This function retrieves the nucleon number
given a particular isotope.
"""
def nuclide_nucleon_number(isotope, result_box):
    nuc = rd.Nuclide(isotope)
    result = nuc.A
    edit_result(result, result_box)

"""
This function retrieves the atomic mass
given a particular isotope.
The result is then converted to the desired units.
"""
def nuclide_atomic_mass(isotope, result_box):
    # Gets atomic mass units from user prefs
    db_path = get_user_data_path("Settings/General/Isotopes")
    with shelve.open(db_path) as prefs:
        num = prefs.get("am_num", "g")
        den = prefs.get("am_den", "mol")

    nuc = rd.Nuclide(isotope)
    result = nuc.atomic_mass
    result *= atomic_mass_numerator[num]
    result /= atomic_mass_denominator[den]
    edit_result(result, result_box, num, den)