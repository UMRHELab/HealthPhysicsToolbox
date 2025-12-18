##### IMPORTS #####
import json
import pandas as pd
from Utility.Functions.gui_utility import no_selection
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
def export_data(root, item, rad_types, isotope, error_label):
    root.focus()

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
    type_col = "Type"
    yield_col = "Yield"
    energy_col = "Energy (MeV)"
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

    save_file(df, "Data", error_label, item, "energies")