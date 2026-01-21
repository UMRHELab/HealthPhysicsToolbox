##### IMPORTS #####
import io
import csv
import shelve
import pandas as pd
import matplotlib.pyplot as plt
from Utility.Functions.logic_utility import get_unit
from Utility.Functions.gui_utility import no_selection
from Utility.Functions.choices import element_choices, material_choices
from Utility.Functions.files import save_file, resource_path, get_user_data_path
from Core.Shielding.Alphas.alphas_calculations import csda_numerator, csda_denominator
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

    # Gets units and linear selector from user prefs
    db_path = get_user_data_path("Settings/Shielding/Alphas")
    with shelve.open(db_path) as prefs:
        csda_num = prefs.get("csda_num", "g")
        d_num = prefs.get("d_num", "g")
        csda_den = prefs.get("csda_den", "cm\u00B2")
        d_den = prefs.get("d_den", "cm\u00B3")
        energy_unit = prefs.get("energy_unit", "MeV")
        linear = prefs.get("linear", False)

    # Gets applicable units
    num_units = [csda_num, d_num]
    den_units = [csda_den, d_den]
    mode_choices = ["CSDA Range",
                    "Density"]
    num = get_unit(num_units, mode_choices, mode)
    den = get_unit(den_units, mode_choices, mode)

    # Error-check for no selected item
    if item == "":
        error_label.config(style="Error.TLabel", text=no_selection)
        return

    error_label.config(style="Error.TLabel", text="")

    # Sets up columns for dataframe
    energy_col = "Alpha Energy (" + energy_unit + ")"
    unit = " (" + num + "/" + den + ")"
    if linear:
        unit = " (" + den.split("\u00B2", 1)[0] + ")"
    mode_col = mode + unit
    cols = [energy_col, mode_col]

    df = pd.DataFrame(columns=cols)
    if category in element_choices:
        # Load the CSV file
        db_path = resource_path('Data/NIST Coefficients/Alphas/Elements/' + item + '.csv')
        df2 = pd.read_csv(db_path)

        df[energy_col] = df2["Alpha Energy"]
        df[mode_col] = df2[mode]
    elif category in material_choices:
        db_path = resource_path('Data/General Data/Material Composition/' + item + '.csv')
        with open(db_path, 'r') as file:
            make_df_for_material(file, df, item, category, mode)
    else:
        db_path = get_user_data_path('Custom Materials/_' + item)
        with shelve.open(db_path) as db:
            stored_data = db[item]
            stored_data = stored_data.replace('\\n', '\n')

        # Create file-like object from the stored string
        csv_file_like = io.StringIO(stored_data)

        make_df_for_material(csv_file_like, df, item, category, mode)

    # Converts energy column to desired energy unit
    df[energy_col] /= energy_units[energy_unit]

    # Convert to desired unit
    df[mode_col] *= csda_numerator[num]
    df[mode_col] /= csda_denominator[den]
    if linear:
        density = find_density(category, item)
        density *= density_numerator[num]
        density /= density_denominator[den.split("\u00B2", 1)[0] + "\u00B3"]
        df[mode_col] /= density

    if choice == "Plot":
        configure_plot(df, energy_col, mode_col, item)
        if save == 1:
            save_file(plt, choice, error_label, item, "range")
        else:
            error_label.config(style="Success.TLabel", text=choice + " exported!")
            plt.show()
    else:
        save_file(df, choice, error_label, item, "range")

#####################################################################################
# PLOT SECTION
#####################################################################################

"""
This function configures the plot that is being exported
using the dataframe and other information.
First, the plot is cleared from any previous exports.
Then, we plot the mode column against the data column.
The title and axis titles are all configured
and the axis scales are set to logarithmic.
"""
def configure_plot(df, energy_col, mode_col, item):
    # Clear from past plots
    plt.clf()

    # Plot the data
    plt.plot(df[energy_col], df[mode_col], marker='o', label=mode_col)
    plt.title(item + " - " + mode_col, fontsize=8.5)
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel(energy_col)
    plt.ylabel(mode_col)
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()

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
calculation mode value by calling the find_data function
with the mode.
"""
def make_df_for_material(file_like, df, material, category, mode):
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
        x = find_data(category, mode, material, val, "Alphas")
        row = [val, x]
        df.loc[index] = row