##### IMPORTS #####
import json
import shelve
import pandas as pd
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
   No selected item
   No radiation types selected
If the error is not applicable, a dataframe is set up
with columns for radiation type, yield, and energy.
The dataframe is populated from the icrp-07.json file.
Finally, we pass on the work to the save_file function.
"""
def export_data(root, item, rad_types, isotope, error_label, sort_column, sort_order):
    root.focus()

    # Gets energy unit from user prefs
    db_path = get_user_data_path("Settings/Decay/Information")
    with shelve.open(db_path) as prefs:
        energy_unit = prefs.get("energy_unit", "MeV")

    # Error-check for no selected item
    if item == "":
        error_label.config(style="Error.TLabel", text=no_selection)
        return

    # Error-check for no radiation types selected
    if len(rad_types) == 0:
        error_label.config(style="Error.TLabel", text="Error: No radiation types selected.")
        return

    error_label.config(style="Error.TLabel", text="")

    # Sets up columns for dataframe
    type_col = "Radiation Type"
    yield_col = "Yield"
    energy_col = "Energy (" + energy_unit + ")"
    cols = [type_col, yield_col, energy_col]

    df = pd.DataFrame(columns=cols)

    db_path = resource_path('Data/Radioactive Decay/icrp-07.json')
    with open(db_path, 'r') as file:
        # Retrieves data
        data = json.load(file).get(isotope, -1)

        # Error-check for missing data
        if data == -1:
            error_label.config(style="Error.TLabel", text="No data for "+isotope+".")
            return

        # Populates dataframe
        for index, rad in enumerate(data["radiations"]):
            if rad["type"] in rad_types:
                df.loc[index] = {type_col : rad["type"],
                                 yield_col : rad["yield"],
                                 energy_col : rad["energy_MeV"]}

    # Converts energy column to desired energy unit
    df[energy_col] /= energy_units[energy_unit]

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