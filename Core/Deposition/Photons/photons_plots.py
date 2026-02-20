##### IMPORTS #####
import io
import math
import shelve
import pandas as pd
import matplotlib.pyplot as plt
from Utility.Functions.plot import configure_plot
from Utility.Functions.logic_utility import get_unit
from Utility.Functions.gui_utility import no_selection
from Utility.Functions.choices import element_choices, material_choices
from Utility.Functions.math_utility import make_df_for_material, energy_units
from Utility.Functions.files import save_file, resource_path, get_user_data_path
from Core.Deposition.Photons.photons_calculations import mea_numerator, mea_denominator

#####################################################################################
# EXPORT SECTION
#####################################################################################

"""
This function is called when the Export button is hit.
The function handles the following errors:
   No selected item
If the error is not applicable, a dataframe is set up
with a column for energy as well as a column for the mode.
If we are working with an element, we copy these columns
from the raw data, converting the energy column to the
desired energy unit. Otherwise, we pass on the work of
filling out the dataframe to the make_df_for_material function.
Once the dataframe is filled out, we convert the mode column
to the desired unit.
Then, if the selected export type is Plot, we call
configure_plot.
Finally, if the file is meant to be saved, we pass on the
work to the save_file function. Otherwise, we show the plot.
"""
def export_data(root, item, category, mode, choice, save, error_label):
    root.focus()

    # Gets units from user prefs
    db_path = get_user_data_path("Settings/Deposition/Photons")
    with shelve.open(db_path) as prefs:
        mea_num = prefs.get("mea_num", "cm\u00B2")
        d_num = prefs.get("d_num", "g")
        mea_den = prefs.get("mea_den", "g")
        d_den = prefs.get("d_den", "cm\u00B3")
        energy_unit = prefs.get("energy_unit", "MeV")

    # Gets applicable units
    num_units = [mea_num, d_num]
    den_units = [mea_den, d_den]
    mode_choices = ["Mass Energy-Absorption",
                    "Density"]
    num = get_unit(num_units, mode_choices, mode)
    den = get_unit(den_units, mode_choices, mode)

    # Error-check for no selected item
    if item == "":
        error_label.config(style="Error.TLabel", text=no_selection)
        return

    error_label.config(style="Error.TLabel", text="")

    # Sets up columns for dataframe
    energy_col = "Photon Energy (" + energy_unit + ")"
    unit = " (" + num + "/" + den + ")"
    mode_col = mode + unit
    cols = [energy_col, mode_col]

    df = pd.DataFrame(columns=cols)
    if category in element_choices:
        # Load the CSV file
        db_path = resource_path('Data/NIST Coefficients/Photons/Elements/' + item + '.csv')
        df2 = pd.read_csv(db_path)

        df[energy_col] = df2["Photon Energy"]
        df[mode_col] = df2[mode]

        # Removes empty rows
        for index, row in df.iterrows():
            if math.isnan(row[mode_col]):
                df.drop(index=index, inplace=True)
    elif category in material_choices:
        db_path = resource_path('Data/General Data/Material Composition/' + item + '.csv')
        with open(db_path, 'r') as file:
            make_df_for_material(file, df, item, category, mode, energy_unit,
                                 "Photons")
    else:
        db_path = get_user_data_path('Custom Materials/_' + item)
        with shelve.open(db_path) as db:
            stored_data = db[item]
            stored_data = stored_data.replace('\\n', '\n')

        # Create file-like object from the stored string
        csv_file_like = io.StringIO(stored_data)

        make_df_for_material(csv_file_like, df, item, category, mode, energy_unit,
                             "Photons")

    # Converts energy column to desired energy unit
    df[energy_col] /= energy_units[energy_unit]

    # Convert to desired unit
    df[mode_col] *= mea_numerator[num]
    df[mode_col] /= mea_denominator[den]

    if choice == "Plot":
        configure_plot(None, df, energy_col, mode_col, f"{item} - {mode_col}")
        if save == 1:
            save_file(plt, choice, error_label, item, "absorption")
        else:
            error_label.config(style="Success.TLabel", text=choice + " exported!")
            plt.show()
    else:
        save_file(df, choice, error_label, item, "absorption")