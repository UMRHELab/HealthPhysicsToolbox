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
csda_numerator = {"mg" : 1000, "g" : 1, "kg" : 0.001}
csda_denominator = {"mm\u00B2" : 10 ** 2, "cm\u00B2" : 1,
                    "m\u00B2" : 0.01 ** 2}

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
def handle_calculation(root, category, mode, item, energy_str,
                       result_box, range_result):
    root.focus()

    # Gets units from user prefs
    db_path = get_user_data_path("Settings/Shielding/Alphas")
    with shelve.open(db_path) as prefs:
        csda_num = prefs.get("csda_num", "g")
        d_num = prefs.get("d_num", "g")
        csda_den = prefs.get("csda_den", "cm\u00B2")
        d_den = prefs.get("d_den", "cm\u00B3")
        energy_unit = prefs.get("energy_unit", "MeV")

    # Gets applicable units
    num_units = [csda_num, d_num]
    den_units = [csda_den, d_den]
    mode_choices = ["CSDA Range",
                    "Density"]
    num = get_unit(num_units, mode_choices, mode)
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

    if mode == "Density":
        result = find_density(category, item)
        result2 = 0
    else:
        result = find_data(category, mode, item, energy_target, "Alphas")
        result2 = find_density(category, item)

    # Displays result label
    if not result in errors:
        # Converts result to desired units
        if mode == "CSDA Range":
            result *= csda_numerator[num]
            result /= csda_denominator[den]
            result2 *= density_numerator[num]
            result2 /= density_denominator[den.split("\u00B2", 1)[0] + "\u00B3"]
            edit_result(f"{(result/result2):.4g} {den.split("\u00B2", 1)[0]}", range_result)
        else:
            result *= density_numerator[num]
            result /= density_denominator[den]
        edit_result(f"{result:.4g}", result_box, num=num, den=den)
    else:
        edit_result(result, result_box)