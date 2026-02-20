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
from Core.Deposition.Electrons.electrons_calculations import (
    sp_e_numerator,
    sp_l_numerator,
    sp_denominator
)
from Utility.Functions.math_utility import (
    make_df_for_material,
    find_density, energy_units,
    density_numerator, density_denominator
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
columns to the desired unit.
Then, if the selected export type is Plot, we call
configure_plot.
Finally, if the file is meant to be saved, we pass on the
work to the save_file function. Otherwise, we show the plot.
"""
def export_data(root, item, category, mode, interactions, choice, save, error_label):
    root.focus()

    # Gets units and linear selector from user prefs
    db_path = get_user_data_path("Settings/Deposition/Electrons")
    with shelve.open(db_path) as prefs:
        sp_e_num = prefs.get("sp_e_num", "MeV")
        sp_l_num = prefs.get("sp_l_num", "cm\u00B2")
        d_num = prefs.get("d_num", "g")
        sp_den = prefs.get("sp_den", "g")
        d_den = prefs.get("d_den", "cm\u00B3")
        energy_unit = prefs.get("energy_unit", "MeV")
        linear = prefs.get("linear", False)

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
        error_label.config(style="Error.TLabel", text=no_selection)
        return

    # Error-check for no interactions selected
    if mode == "Mass Stopping Power" and len(interactions) == 0:
        error_label.config(style="Error.TLabel", text="Error: No interactions selected.")
        return

    error_label.config(style="Error.TLabel", text="")

    # Sets up columns for dataframe
    energy_col = "Electron Energy (" + energy_unit + ")"
    cols = [energy_col]
    if mode == "Mass Stopping Power":
        for interaction in interactions:
            cols.append(interaction)
    else:
        cols.append(mode)

    df = pd.DataFrame(columns=cols)
    if category in element_choices:
        # Load the CSV file
        db_path = resource_path('Data/NIST Coefficients/Electrons/Elements/' + item + '.csv')
        df2 = pd.read_csv(db_path)

        df[energy_col] = df2["Kinetic Energy"]

        if mode == "Mass Stopping Power":
            for interaction in interactions:
                df[interaction] = df2[interaction]
        else:
            df[mode] = df2[mode]
    elif category in material_choices:
        db_path = resource_path('Data/General Data/Material Composition/' + item + '.csv')
        with open(db_path, 'r') as file:
            make_df_for_material(file, df, item, category, mode, energy_unit,
                                 "Electrons", interactions=interactions if mode == "Mass Stopping Power" else None)
    else:
        db_path = get_user_data_path('Custom Materials/_' + item)
        with shelve.open(db_path) as db:
            stored_data = db[item]
            stored_data = stored_data.replace('\\n', '\n')

        # Create file-like object from the stored string
        csv_file_like = io.StringIO(stored_data)

        make_df_for_material(csv_file_like, df, item, category, mode, energy_unit,
                             "Electrons", interactions=interactions if mode == "Mass Stopping Power" else None)

    # Converts energy column to desired energy unit
    df[energy_col] /= energy_units[energy_unit]

    # Convert to desired unit
    if mode == "Mass Stopping Power":
        density_mult = 1
        if linear:
            density_mult = find_density(category, item)
            density_mult *= density_numerator[den]
            density_mult /= density_denominator[num_l.split("\u00B2", 1)[0] + "\u00B3"]
        for interaction in interactions:
            df[interaction] *= sp_e_numerator[num_e]
            df[interaction] *= sp_l_numerator[num_l]
            df[interaction] /= sp_denominator[den]
            df[interaction] *= density_mult

    unit = " (" + num + "/" + den + ")"
    mode_col = mode
    if mode == "Mass Stopping Power":
        if linear:
            unit = " (" + num_e + "/" + num_l.split("\u00B2", 1)[0] + ")"
        mode_col += unit

    if choice == "Plot":
        interactions_for_plot = interactions if mode == "Mass Stopping Power" else None
        configure_plot(interactions_for_plot, df, energy_col, mode_col, f"{item} - {mode_col}")
        if save == 1:
            save_file(plt, choice, error_label, item, "stopping")
        else:
            error_label.config(style="Success.TLabel", text=choice + " exported!")
            plt.show()
    else:
        if mode == "Mass Stopping Power":
            for interaction in interactions:
                df.rename(columns={interaction: interaction+unit}, inplace=True)
        save_file(df, choice, error_label, item, "stopping")