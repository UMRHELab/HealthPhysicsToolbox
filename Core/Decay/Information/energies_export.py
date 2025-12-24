##### IMPORTS #####
import math
import json
import shelve
import pandas as pd
import radioactivedecay as rd
from Utility.Functions.files import get_user_data_path
from Utility.Functions.gui_utility import no_selection
from Utility.Functions.math_utility import energy_units
from Utility.Functions.files import save_file, resource_path

#####################################################################################
# EXPORT SECTION
#####################################################################################

"""
This function is called when the Export button is hit.
The function handles the following error:
   No selected element
   Isotope is stable
   No radiation types selected
   Non-number yield threshold input
   Non-number energy threshold input
   Yield threshold cannot be negative
   Energy threshold cannot be negative
   Yield minimum cannot be more than yield maximum
   Energy minimum cannot be more than energy maximum
If the error is not applicable, a dataframe is set up
with columns for radiation type, yield, and energy.
The dataframe is populated from the corresponding energies
.json file.
Finally, we pass on the work to the save_file function.
"""
def export_data(root, element, rad_types, isotope, error_label, sort_column, sort_order,
                yield_min, yield_max, energy_min, energy_max):
    root.focus()

    # Gets energy unit from user prefs
    db_path = get_user_data_path("Settings/Decay/Information")
    with shelve.open(db_path) as prefs:
        energy_unit = prefs.get("energy_unit", "MeV")

    # Error-check for no selected element
    if element == "":
        error_label.config(style="Error.TLabel", text=no_selection)
        return

    # Error-check for isotope is stable
    if math.isinf(rd.Nuclide(isotope).half_life('s')):
        error_label.config(style="Error.TLabel", text=isotope+" is stable.")
        return

    # Error-check for no radiation types selected
    if len(rad_types) == 0:
        error_label.config(style="Error.TLabel", text="Error: No radiation types selected.")
        return

    # Error-check for non-number yield threshold input
    if yield_min is None or yield_max is None:
        error_label.config(style="Error.TLabel", text="Error: Non-number yield threshold input.")
        return

    # Error-check for non-number energy threshold input
    if energy_min is None or energy_max is None:
        error_label.config(style="Error.TLabel", text="Error: Non-number energy threshold input.")
        return

    # Error-check for negative yield threshold
    if yield_min < 0 or yield_max < 0:
        error_label.config(style="Error.TLabel", text="Error: Yield threshold cannot be negative.")
        return

    # Error-check for negative energy threshold
    if energy_min < 0 or energy_max < 0:
        error_label.config(style="Error.TLabel", text="Error: Energy threshold cannot be negative.")
        return

    # Error-check for minimum yield more than maximum yield
    if yield_min > yield_max:
        error_label.config(style="Error.TLabel", text="Error: Yield minimum cannot be more than yield maximum.")
        return

    # Error-check for minimum energy more than maximum energy
    if energy_min > energy_max:
        error_label.config(style="Error.TLabel", text="Error: Energy minimum cannot be more than energy maximum.")
        return

    error_label.config(style="Error.TLabel", text="")

    # Sets up columns for dataframe
    type_col = "Radiation Type"
    yield_col = "Yield"
    energy_col = "Energy (" + energy_unit + ")"
    cols = [type_col, yield_col, energy_col]

    df = pd.DataFrame(columns=cols)

    # Energy unit divisor
    divisor = energy_units[energy_unit]

    db_path = resource_path('Data/Radioactive Decay/Energies/'+element+'.json')
    import os
    for entry in os.listdir('Data/Radioactive Decay/Energies/'):
        full_path = os.path.join('Data/Radioactive Decay/Energies/', entry)
        if os.path.isfile(full_path):
            print(entry)
    with open(db_path, 'r') as file:
        # Retrieves data
        data = json.load(file).get(isotope, -1)

        # Error-check for missing data
        if data == -1:
            error_label.config(style="Error.TLabel", text="No data for "+isotope+".")
            return

        # Populates dataframe and converts energy to desired energy unit
        for index, rad in enumerate(data["radiations"]):
            energy = rad["energy_MeV"] / divisor
            if rad["type"] in rad_types and \
               yield_min <= rad["yield"] <= yield_max and \
               energy_min <= energy <= energy_max:
                df.loc[index] = {type_col : rad["type"],
                                 yield_col : rad["yield"],
                                 energy_col : energy}

    # List of radiation types
    rad_types = [
        "Gamma Ray",                      "Prompt Gamma Ray",
        "Delayed Gamma Ray",              "Annihilation Photon",
        "X-Ray",                          "Beta- Particle",
        "Delayed Beta Particle",          "Beta+ Particle",
        "Internal Conversion Electron",   "Auger Electron",
        "Alpha Particle",                 "Alpha Recoil Nucleus",
        "Fission Fragment",               "Neutron",
    ]


    # Create temporary column for radiation type sorting
    rad_order = {rad: i for i, rad in enumerate(rad_types)}
    temp_col = "rad_order"
    df[temp_col] = df[type_col].map(rad_order)

    # Configure sort order
    by = []
    ascending = []
    sort_order = sort_order == "Ascending"
    if sort_column == type_col:
        by = [temp_col, yield_col, energy_col]
        ascending = [sort_order, False, True]
    elif sort_column == yield_col:
        by = [yield_col, temp_col, energy_col]
        ascending = [sort_order, True, True]
    elif sort_column == energy_col.split(' ')[0]:
        by = [energy_col, temp_col, yield_col]
        ascending = [sort_order, True, False]

    # Sort dataframe
    df.sort_values(by=by, ascending=ascending, inplace=True)

    # Drop temporary column
    df.drop(columns=[temp_col], inplace=True)

    save_file(df, "Data", error_label, isotope, "energies")