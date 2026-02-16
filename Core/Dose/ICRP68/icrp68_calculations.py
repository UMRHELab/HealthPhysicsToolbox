##### IMPORTS #####
import csv
import shelve
from tkinter import END
from Utility.Functions.gui_utility import edit_result, no_selection
from Utility.Functions.files import resource_path, get_user_data_path

#####################################################################################
# UNITS SECTION
#####################################################################################

# Unit choices paired with their factor in relation to the default
Bq_TO_Ci = 1 / 3.7e10
dose_numerator = {"pSv" : 10 ** 12, "nSv" : 10 ** 9,
                  "μSv" : 10 ** 6, "mSv" : 10 ** 3,
                  "Sv" : 1, "μrem" : 100 * (10 ** 6),
                  "mrem" : 100 * (10 ** 3), "rem" : 100}
dose_denominator = {"Bq" : 1, "kBq" : 10 ** -3,
                    "MBq" : 10 ** -6, "GBq" : 10 ** -9,
                    "pCi" : Bq_TO_Ci * (10 ** 12), "nCi" : Bq_TO_Ci * (10 ** 9),
                    "μCi" : Bq_TO_Ci * (10 ** 6), "mCi" : Bq_TO_Ci * (10 ** 3),
                    "Ci" : Bq_TO_Ci}

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
def handle_calculation(root, mode, coefficient, intake_str, result_box, dose_result):
    root.focus()

    # Gets isotope, units, and dose selector from user prefs
    db_path = get_user_data_path(f"Settings/Dose/ICRP68")
    with shelve.open(db_path) as prefs:
        isotope = prefs.get("isotope", "")
        num = prefs.get("dose_unit", "Sv")
        den = prefs.get("intake_unit", "Bq")
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

    # Converts result to desired units
    if coefficient != "Half Life" and coefficient != "f1":
        results = [float(result) for result in results]
        results = [result * dose_numerator[num] for result in results]
        results = [result / dose_denominator[den] for result in results]
        intake /= dose_denominator[den]
    elif results and coefficient == "Half Life":
        results = [results[0]]

    # Fills result box
    if results:
        if coefficient == "Half Life" or coefficient == "f1":
            for result in results:
                result_box.insert(END, f"{result}\n")
        else:
            for result in results:
                result_box.insert(END, f"{result:.4g} {num}/{den}\n")
                if dose:
                    dose_result.insert(END, f"{result * intake:.4g} {num}\n")
        result_box.config(state="disabled", height=len(results))
        dose_result.config(state="disabled", height=len(results))
    else:
        edit_result("Error: Invalid request.", result_box)