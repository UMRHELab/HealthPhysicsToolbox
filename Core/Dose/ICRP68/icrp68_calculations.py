##### IMPORTS #####
import csv
from tkinter import END
from Utility.Functions.files import resource_path
from Utility.Functions.gui_utility import edit_result, no_selection

#####################################################################################
# CALCULATIONS SECTION
#####################################################################################

"""
This function is called when the Calculate button is hit.
The function handles the following error:
   No selected element
If the error is not applicable, the coefficient
is retrieved from the database, and then
displayed in the result label.
"""
def handle_calculation(root, mode, coefficient, isotope, result_box):
    root.focus()

    # Clears result box
    result_box.config(state="normal")
    result_box.delete("1.0", END)

    # Error-check for no selected element
    if isotope == "":
        edit_result(no_selection, result_box)
        return

    results = []

    # Finds coefficient
    db_path = resource_path('Data/ICRP Coefficients/ICRP68/' + mode + '.csv')
    with open(db_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["Nuclide"] == isotope:
                for key, val in row.items():
                    if key == coefficient:
                        results.append(val)

    # Converts to float
    if coefficient != "Half Life" and coefficient != "f1":
        results = [float(result) for result in results]
    elif results and coefficient == "Half Life":
        results = [results[0]]

    # Fills result box
    if results:
        if coefficient == "Half Life" or coefficient == "f1":
            for result in results:
                result_box.insert(END, f"{result}\n")
        else:
            for result in results:
                result_box.insert(END, f"{result:.4g} Sv/Bq\n")
        result_box.config(state="disabled", height=len(results))
    else:
        edit_result("Error: Invalid request.", result_box)