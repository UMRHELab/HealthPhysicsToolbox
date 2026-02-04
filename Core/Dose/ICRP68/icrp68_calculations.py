##### IMPORTS #####
import csv
import shelve
from tkinter import END
from Utility.Functions.gui_utility import edit_result, no_selection
from Utility.Functions.files import resource_path, get_user_data_path

#####################################################################################
# CALCULATIONS SECTION
#####################################################################################

"""
This function is called when the Calculate button is hit.
The function handles the following errors:
   No selected element
   Non-number intake input
If the error is not applicable, the coefficient
is retrieved from the database, and then
displayed in the result label.
"""
def handle_calculation(root, mode, coefficient, isotope, intake_str, result_box, dose_result):
    root.focus()

    # Gets dose selector from user prefs
    db_path = get_user_data_path("Settings/Dose/ICRP68")
    with shelve.open(db_path) as prefs:
        dose = prefs.get("dose", False)

    # Clears result box
    result_box.config(state="normal")
    result_box.delete("1.0", END)

    # Clears dose box
    dose_result.config(state="normal")
    dose_result.delete("1.0", END)

    # Error-check for no selected element
    if isotope == "":
        edit_result(no_selection, result_box)
        return

    # Intake input in float format
    intake = 0.0

    if (coefficient != "Half Life" and coefficient != "f1") and dose:
        # Error-check for a non-number intake input
        try:
            intake = float(intake_str)
        except ValueError:
            edit_result("Error: Non-number intake input.", result_box)
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
                if dose:
                    dose_result.insert(END, f"{result * intake:.4g} Sv\n")
        result_box.config(state="disabled", height=len(results))
        dose_result.config(state="disabled", height=len(results))
    else:
        edit_result("Error: Invalid request.", result_box)