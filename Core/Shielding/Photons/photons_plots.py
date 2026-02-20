##### IMPORTS #####
import io
import shelve
import pandas as pd
import matplotlib.pyplot as plt
from Utility.Functions.plot import configure_plot
from Utility.Functions.logic_utility import get_unit
from Utility.Functions.gui_utility import no_selection
from Utility.Functions.choices import element_choices, material_choices
from Utility.Functions.files import save_file, resource_path, get_user_data_path
from Utility.Functions.math_utility import make_df_for_material, find_density, energy_units
from Core.Shielding.Photons.photons_calculations import (
    mac_numerator, mac_denominator,
    lac_numerator, lac_denominator
)

#####################################################################################
# EXPORT SECTION
#####################################################################################

"""
This function is called when the Export button is hit.
The function handles the following errors:
   No selected item
   No interactions selected
If neither error is applicable, a dataframe is set up
with a column for energy as well as a column for each of
the selected interactions.
If we are working with an element, we copy these columns
from the raw data, converting the energy column to the
desired energy unit. Otherwise, we pass on the work of
filling out the dataframe to the make_df_for_material function.
Once the dataframe is filled out, we convert the interaction
columns to the desired unit. If L.A.C. is the selected
calculation mode, we also need to multiply the interaction
columns by the item's density.
Then, if the selected export type is Plot, we call
configure_plot.
Finally, if the file is meant to be saved, we pass on the
work to the save_file function. Otherwise, we show the plot.
"""
def export_data(root, item, category, mode, interactions, choice, save, error_label):
    root.focus()

    # Gets units from user prefs
    db_path = get_user_data_path("Settings/Shielding/Photons")
    with shelve.open(db_path) as prefs:
        mac_num = prefs.get("mac_num", "cm\u00B2")
        d_num = prefs.get("d_num", "g")
        lac_num = prefs.get("lac_num", "1")
        mac_den = prefs.get("mac_den", "g")
        d_den = prefs.get("d_den", "cm\u00B3")
        lac_den = prefs.get("lac_den", "cm")
        energy_unit = prefs.get("energy_unit", "MeV")

    # Gets applicable units
    num_units = [mac_num, d_num, lac_num]
    den_units = [mac_den, d_den, lac_den]
    mode_choices = ["Mass Attenuation Coefficient",
                    "Density",
                    "Linear Attenuation Coefficient"]
    num = get_unit(num_units, mode_choices, mode)
    den = get_unit(den_units, mode_choices, mode)

    # Error-check for no selected item
    if item == "":
        error_label.config(style="Error.TLabel", text=no_selection)
        return

    # Error-check for no interactions selected
    if len(interactions) == 0:
        error_label.config(style="Error.TLabel", text="Error: No interactions selected.")
        return

    error_label.config(style="Error.TLabel", text="")

    # Sets up columns for dataframe
    energy_col = f"Photon Energy ({energy_unit})"
    cols = [energy_col]
    for interaction in interactions:
        cols.append(interaction)

    df = pd.DataFrame(columns=cols)
    if category in element_choices:
        # Load the CSV file
        db_path = resource_path(f'Data/NIST Coefficients/Photons/Elements/{item}.csv')
        df2 = pd.read_csv(db_path)

        df[energy_col] = df2["Photon Energy"]

        for interaction in interactions:
            df[interaction] = df2[interaction]
    elif category in material_choices:
        db_path = resource_path(f'Data/General Data/Material Composition/{item}.csv')
        with open(db_path, 'r') as file:
            make_df_for_material(file, df, item, category, mode, energy_unit,
                                 "Photons", interactions=interactions)
    else:
        db_path = get_user_data_path(f'Custom Materials/_{item}')
        with shelve.open(db_path) as db:
            stored_data = db[item]
            stored_data = stored_data.replace('\\n', '\n')

        # Create file-like object from the stored string
        csv_file_like = io.StringIO(stored_data)

        make_df_for_material(csv_file_like, df, item, category, mode, energy_unit,
                             "Photons", interactions=interactions)

    # Converts energy column to desired energy unit
    df[energy_col] /= energy_units[energy_unit]

    # Convert to desired unit
    if mode == "Mass Attenuation Coefficient":
        for interaction in interactions:
            df[interaction] *= mac_numerator[num]
            df[interaction] /= mac_denominator[den]
    else:
        density = find_density(category, item)
        for interaction in interactions:
            df[interaction] *= density
            df[interaction] *= lac_numerator[num]
            df[interaction] /= lac_denominator[den]

    unit = f"({num}/{den})"
    if num == "1":
        unit = f"({den}\u207B\u00B9)"
    mode_col = f"{mode} {unit}"

    if choice == "Plot":
        configure_plot(interactions, df, energy_col, mode_col, f"{item} - {mode_col}")
        if save == 1:
            save_file(plt, choice, error_label, item, "attenuation")
        else:
            error_label.config(style="Success.TLabel", text=f"{choice} exported!")
            plt.show()
    else:
        for interaction in interactions:
            df.rename(columns={interaction: f"{interaction} {unit}"}, inplace=True)
        save_file(df, choice, error_label, item, "attenuation")