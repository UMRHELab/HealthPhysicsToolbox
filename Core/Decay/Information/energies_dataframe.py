##### IMPORTS #####
import json
import shelve
import pandas as pd
from Utility.Functions.gui_utility import edit_result
from Utility.Functions.math_utility import energy_units
from Utility.Functions.files import get_user_data_path, resource_path

#####################################################################################
# DATAFRAME SECTION
#####################################################################################

"""
This function sets up a dataframe with columns for radiation type,
yield, and energy. The dataframe is populated from the corresponding
energies .json file.
The function handles the following error:
   No data for isotope
If this error is encountered, None is returned. Otherwise, the populated
dataframe is returned.
"""
def create_energies_dataframe(element, isotope, error_label, box = False):
    # List of neutron irrelevant radiation types
    neutron_irrelevant_types = [
        "Gamma Ray", "Annihilation Photon",
        "X-Ray", "Beta- Particle", "Beta+ Particle",
        "Internal Conversion Electron", "Auger Electron",
        "Alpha Particle"
    ]

    # Gets radiation types, column, order, filter type, filter direction,
    # filter percentage, and energy unit from user prefs
    db_path = get_user_data_path("Settings/Decay/Information")
    with shelve.open(db_path) as prefs:
        rad_types = prefs.get("rad_types", [rad_type for rad_type in neutron_irrelevant_types])
        sort_column = prefs.get("column", "Radiation Type")
        sort_order = prefs.get("order", "Ascending")
        filter_type = prefs.get("filter_type", "Yield")
        filter_dir = prefs.get("filter_dir", "Top")
        filter_percentage = prefs.get("filter_percentage", "100")
        energy_unit = prefs.get("energy_unit", "MeV")

    # Already been error-checked
    filter_percentage = float(filter_percentage)

    # Sets up columns for dataframe
    type_col = "Radiation Type"
    yield_col = "Yield"
    energy_col = "Energy (" + energy_unit + ")"
    cols = [type_col, yield_col, energy_col]

    df = pd.DataFrame(columns=cols)

    # Energy unit divisor
    divisor = energy_units[energy_unit]

    db_path = resource_path('Data/Radioactive Decay/Energies/'+element+'.json')
    with open(db_path, 'r') as file:
        # Retrieves data
        data = json.load(file).get(isotope, -1)

        # Error-check for missing data
        if data == -1:
            if box:
                edit_result("No data for "+isotope+".", error_label)
            else:
                error_label.config(style="Error.TLabel", text="No data for "+isotope+".")
            return None

        # Populates dataframe and converts energy to desired energy unit
        for index, rad in enumerate(data["radiations"]):
            energy = rad["energy_MeV"] / divisor
            if rad["type"] in rad_types:
                df.loc[index] = {type_col : rad["type"],
                                 yield_col : rad["yield"],
                                 energy_col : energy}

    # Filter by Yield or by Energy * Yield
    if filter_type == "Yield":
        series = df[yield_col]
    else:
        series = df[yield_col] * df[energy_col]

    # Gets filter quantile
    filter_quantile = filter_percentage / 100

    # Top N% or Bottom N%
    if filter_dir == "Top":
        df = df[series >= series.quantile(1 - filter_quantile)]
    else:
        df = df[series <= series.quantile(filter_quantile)]

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

    return df