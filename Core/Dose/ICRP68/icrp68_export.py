##### IMPORTS #####
import csv
import pandas as pd
from Utility.Functions.files import save_file, resource_path
from Utility.Functions.gui_utility import edit_result, no_selection

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
def export_data(root, mode, element, isotope, result_box):
    root.focus()

    # Error-check for no selected element
    if element == "":
        edit_result(no_selection, result_box)
        return

    # Sets up columns for dataframe
    names_col = "Nuclide"
    values_col = isotope
    cols = [names_col, values_col]

    df = pd.DataFrame(columns=cols)

    # Populates dataframe
    db_path = resource_path('Data/ICRP Coefficients/ICRP68/'+mode+'.csv')
    with open(db_path, 'r') as file:
        reader = csv.DictReader(file)
        filled_first = False
        for row in reader:
            if row["Nuclide"] == isotope:
                if not filled_first:
                    for key, val in row.items():
                        if key != "Nuclide":
                            df.loc[len(df.index)] = [key, val]
                            filled_first = True
                else:
                    df.insert(len(df.columns), isotope+'_', pd.Series(list(row.values())[1:]))
                    df.columns = list(df.columns[:-1]) + [isotope]

    save_file(df, "Data", result_box, isotope, mode.lower(), True)