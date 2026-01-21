##### IMPORTS #####
import io
import csv
import shelve
import pandas as pd
import matplotlib.pyplot as plt
from Utility.Functions.plot import configure_plot
from Utility.Functions.logic_utility import get_unit
from Utility.Functions.gui_utility import no_selection
from Utility.Functions.choices import element_choices, material_choices
from Utility.Functions.files import save_file, resource_path, get_user_data_path
from Core.Deposition.Alphas.alphas_calculations import (
    sp_e_numerator,
    sp_l_numerator,
    sp_denominator
)
from Utility.Functions.math_utility import (
    density_numerator, density_denominator,
    find_data, find_density, energy_units
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
    db_path = get_user_data_path("Settings/Deposition/Alphas")
    with shelve.open(db_path) as prefs:
        sp_e_num = prefs.get("sp_e_num", "MeV")
        sp_l_num = prefs.get("sp_l_num", "cm\u00B2")
        d_num = prefs.get("d_num", "g")
        sp_den = prefs.get("sp_den", "g")
        d_den = prefs.get("d_den", "cm\u00B3")
        energy_unit = prefs.get("energy_unit", "MeV")
        linear = prefs.get("linear", False)

    # Gets applicable units
    num_e_units = [sp_e_num, d_num]
    num_l_units = [sp_l_num, d_num]
    den_units = [sp_den, d_den]
    mode_choices = ["Mass Stopping Power",
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
    if len(interactions) == 0:
        error_label.config(style="Error.TLabel", text="Error: No interactions selected.")
        return

    error_label.config(style="Error.TLabel", text="")

    # Sets up columns for dataframe
    energy_col = "Alpha Energy (" + energy_unit + ")"
    cols = [energy_col]
    for interaction in interactions:
        cols.append(interaction)

    df = pd.DataFrame(columns=cols)
    if category in element_choices:
        # Load the CSV file
        db_path = resource_path('Data/NIST Coefficients/Alphas/Elements/' + item + '.csv')
        df2 = pd.read_csv(db_path)

        df[energy_col] = df2["Alpha Energy"]

        for interaction in interactions:
            df[interaction] = df2[interaction]
    elif category in material_choices:
        db_path = resource_path('Data/General Data/Material Composition/' + item + '.csv')
        with open(db_path, 'r') as file:
            make_df_for_material(file, df, item, category, interactions)
    else:
        db_path = get_user_data_path('Custom Materials/_' + item)
        with shelve.open(db_path) as db:
            stored_data = db[item]
            stored_data = stored_data.replace('\\n', '\n')

        # Create file-like object from the stored string
        csv_file_like = io.StringIO(stored_data)

        make_df_for_material(csv_file_like, df, item, category, interactions)

    # Converts energy column to desired energy unit
    df[energy_col] /= energy_units[energy_unit]

    # Convert to desired unit
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
    if linear:
        unit = " (" + num_e + "/" + num_l.split("\u00B2", 1)[0] + ")"
    mode_col = mode + unit

    if choice == "Plot":
        configure_plot(interactions, df, energy_col, mode_col, f"{item} - {mode_col}")
        if save == 1:
            save_file(plt, choice, error_label, item, "stopping")
        else:
            error_label.config(style="Success.TLabel", text=choice + " exported!")
            plt.show()
    else:
        for interaction in interactions:
            df.rename(columns={interaction: interaction+unit}, inplace=True)
        save_file(df, choice, error_label, item, "stopping")

#####################################################################################
# DATA SECTION
#####################################################################################

"""
This function fills out the dataframe when we are
exporting data for a material. First, we retrieve
the energy values for the dataframe by taking the values
from the raw data of the first element and then removing
any values that are out of range for any of the remaining
elements. Then, for each energy value, we get the corresponding
interaction value for the rest of the row by calling the find_data function
with each interaction.
"""
def make_df_for_material(file_like, df, material, category, interactions):
    # Reads in file
    reader = csv.DictReader(file_like)

    # Create the dataframe
    vals = []
    for row in reader:
        db_path = resource_path('Data/NIST Coefficients/Alphas/Elements/' + row['Element'] + '.csv')
        if len(vals) == 0:
            with open(db_path, 'r') as file:
                # Reads in file
                reader2 = csv.DictReader(file)

                # Gets energy values to use as dots
                for row2 in reader2:
                    vals.append(float(row2["Alpha Energy"]))
        else:
            with open(db_path, 'r') as file:
                # Reads in file
                reader2 = csv.DictReader(file)

                new_vals = []
                # Gets energy values to use as dots
                for row2 in reader2:
                    new_vals.append(float(row2["Alpha Energy"]))
                max_val = max(new_vals)
                min_val = min(new_vals)
                vals = [val for val in vals if min_val <= val <= max_val]

    # Finds the data for mode at each energy value and adds to dataframe
    for index, val in enumerate(vals):
        row = [val]
        for interaction in interactions:
            x = find_data(category, interaction, material, val, "Alphas")
            row.append(x)
        df.loc[index] = row