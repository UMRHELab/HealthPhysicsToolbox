##### IMPORTS #####
import shelve
from Utility.Functions.logic_utility import get_unit
from Utility.Functions.files import get_user_data_path
from Utility.Functions.gui_utility import edit_result, non_number, no_selection
from Utility.Functions.math_utility import (
    density_numerator, density_denominator,
    find_data, find_density, errors, energy_units
)

#####################################################################################
# UNITS SECTION
#####################################################################################

# Unit choices paired with their factor in relation to the default
sp_e_numerator = {"eV" : 1000 ** 2, "keV" : 1000,
                  "MeV" : 1, "GeV" : 0.001}
sp_l_numerator = {"mm\u00B2" : 10 ** 2, "cm\u00B2" : 1,
                  "m\u00B2" : 0.01 ** 2}
sp_denominator = {"mg" : 1000, "g" : 1, "kg" : 0.001}

#####################################################################################
# CALCULATIONS SECTION
#####################################################################################

"""
This function is called when the Calculate button is hit.
The function handles the following errors:
   No selected item
   Non-number energy input
If neither error is applicable, the energy input
is converted to MeV to match the raw data.
Then, the function decides what calculation to perform
based on the selected calculation mode.
Finally, if the calculation did not cause an error,
the result is converted to the desired units, and then
displayed in the result label.
"""
def handle_calculation(root, category, mode, interactions, item,
                       energy_str, result_box, range_result):
    root.focus()

    # Gets units from user prefs
    db_path = get_user_data_path("Settings/Deposition/Electrons")
    with shelve.open(db_path) as prefs:
        sp_e_num = prefs.get("sp_e_num", "MeV")
        sp_l_num = prefs.get("sp_l_num", "cm\u00B2")
        d_num = prefs.get("d_num", "g")
        sp_den = prefs.get("sp_den", "g")
        d_den = prefs.get("d_den", "cm\u00B3")
        energy_unit = prefs.get("energy_unit", "MeV")

    # Gets applicable units
    num_e_units = [sp_e_num, "", "", d_num]
    num_l_units = [sp_l_num, "", "", d_num]
    den_units = [sp_den, "", "", d_den]
    mode_choices = ["Mass Stopping Power",
                    "Radiation Yield",
                    "Density Effect Delta",
                    "Density"]
    num_e = get_unit(num_e_units, mode_choices, mode)
    num_l = get_unit(num_l_units, mode_choices, mode)
    num = num_e + " * " + num_l if mode == "Mass Stopping Power" else num_e
    den = get_unit(den_units, mode_choices, mode)

    # Error-check for no selected item
    if item == "":
        edit_result(no_selection, result_box)
        return

    # Energy input in float format
    energy_target = 0.0

    if mode != "Density":
        # Error-check for a non-number energy input
        try:
            energy_target = float(energy_str)
        except ValueError:
            edit_result(non_number, result_box)
            return

    # Converts energy_target to MeV to comply with the raw data
    energy_target *= energy_units[energy_unit]
    result = 0

    if mode == "Mass Stopping Power":
        for interaction in interactions:
            datum = find_data(category, interaction, item, energy_target, "Electrons")
            if datum in errors:
                result = datum
                break
            result += datum
        result2 = find_density(category, item)
    elif mode == "Density":
        result = find_density(category, item)
        result2 = 0
    else:
        result = find_data(category, mode, item, energy_target, "Electrons")
        result2 = 0

    # Displays result label
    if not result in errors:
        # Converts result to desired units
        if mode == "Mass Stopping Power":
            result *= sp_e_numerator[num_e]
            result *= sp_l_numerator[num_l]
            result /= sp_denominator[den]
            result2 *= density_numerator[den]
            lin_den = num_l.split("\u00B2", 1)[0]
            result2 /= density_denominator[lin_den + "\u00B3"]
            edit_result(f"{(result*result2):.4g} {num_e}/{lin_den}", range_result)
        elif mode == "Density":
            result *= density_numerator[num]
            result /= density_denominator[den]
        edit_result(f"{result:.4g}", result_box, num=num, den=den)
    else:
        edit_result(result, result_box)