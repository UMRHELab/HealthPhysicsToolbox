##### IMPORTS #####
import csv
import shelve
import pandas as pd
from Utility.Functions.choices import get_successors
from Utility.Functions.gui_utility import no_selection
from Utility.Functions.files import save_file, resource_path, get_user_data_path

#####################################################################################
# EXPORT SECTION
#####################################################################################

"""
This function is called when the Calculate button is hit.
The function handles the following error:
   No selected element
If the error is not applicable, a dataframe is set up
with the ICRP68 coefficients for the selected nuclide.
The dataframe is populated from the corresponding ICRP68 file.
Finally, we pass on the work to the save_file function.
"""
def export_data(root, mode, daughters, error_label):
    root.focus()

    # Gets isotope from user prefs
    db_path = get_user_data_path(f"Settings/Dose/ICRP68")
    with shelve.open(db_path) as prefs:
        isotope = prefs.get("isotope", "")

    # Error-check for no selected element
    if isotope == "":
        error_label.config(style="Error.TLabel", text=no_selection)
        return

    error_label.config(text="")

    # Gets successors of isotope
    isotopes = get_successors(isotope) if daughters else [isotope]

    df = pd.DataFrame()
    rows = []

    # Gets rows
    db_path = resource_path('Data/ICRP Coefficients/ICRP68/' + mode + '.csv')
    with open(db_path, 'r') as file:
        reader = csv.DictReader(file)

        for row in reader:
            rows = list(row.keys())
            break
        df.insert(0, "Nuclide", pd.Series(rows[1:]))

    # Populates dataframe
    with open(db_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["Nuclide"] in isotopes:
                df.insert(len(df.columns), row["Nuclide"]+'_', pd.Series(list(row.values())[1:]))
                df.columns = list(df.columns[:-1]) + [row["Nuclide"]]

    save_file(df, "Data", error_label, isotope, mode.lower(), False)