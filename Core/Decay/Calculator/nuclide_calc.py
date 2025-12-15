##### IMPORTS #####
import math
import shelve
import tkinter as tk
import radioactivedecay as rd
import matplotlib.pyplot as plt
from Utility.Functions.gui_utility import edit_result
from Utility.Functions.files import get_user_data_path

#####################################################################################
# CALCULATIONS SECTION
#####################################################################################

"""
This function is called when the Calculate button is hit.
The function checks if the time already has an error.
If not, the function decides what calculation to
perform based on the selected calculation mode.
"""
def handle_calculation(root, mode, isotope, initial_amount, time, dates, result_box):
    root.focus()

    # Error-check for invalid time inputs
    if dates:
        if isinstance(time, str) and time[0:5] == "Error":
            edit_result(time, result_box)
            return

    match mode:
        case "Activities":
            nuclide_activities(isotope, initial_amount, time, dates, result_box)
        case "Plot":
            nuclide_plot(isotope, initial_amount, time, dates, result_box)

"""
This function retrieves the activities
given a particular isotope, initial amount, and time.
"""
def nuclide_activities(isotope, initial_amount, time, dates, result_box):
    # Gets units from user prefs
    db_path = get_user_data_path("Settings/Decay/Calculator")
    with shelve.open(db_path) as prefs:
        amount_type = prefs.get("amount_type", "Activity (Bq)")
        amount_unit = prefs.get("amount_unit", "Bq")
        time_unit = prefs.get("time_unit", "s")
    if dates:
        time_unit = "d"

    # Clears result box
    result_box.config(state="normal")
    result_box.delete("1.0", tk.END)

    # Error checks
    if is_error(isotope, time, initial_amount, result_box):
        return
    else:
        time = float(time)
        initial_amount = float(initial_amount)

    # Retrieves activities
    t0 = rd.Inventory({isotope: initial_amount}, amount_unit)
    t1 = t0.decay(time, time_unit)
    if amount_type == "Mass":
        activities = t1.masses(amount_unit)
    elif amount_type == "Moles":
        activities = t1.moles(amount_unit)
    elif amount_type == "Nuclei Number":
        activities = t1.contents
    else:
        activities = t1.activities(amount_unit)

    # Fills result box
    for activity in activities:
        result_box.insert(tk.END, f"{activity}, {activities[activity]:.4g}\n")
    result_box.config(state="disabled", height=len(activities))

"""
This function retrieves the activities plot
given a particular isotope, initial amount, and time.
"""
def nuclide_plot(isotope, initial_amount, time, dates, result_box):
    # Gets units from user prefs
    db_path = get_user_data_path("Settings/Decay/Calculator")
    with shelve.open(db_path) as prefs:
        amount_unit = prefs.get("amount_unit", "Bq")
        time_unit = prefs.get("time_unit", "s")
    if dates:
        time_unit = "d"

    # Clears result box
    result_box.config(state="normal")
    result_box.delete("1.0", tk.END)

    # Error checks
    if is_error(isotope, time, initial_amount, result_box):
        return
    else:
        time = float(time)
        initial_amount = float(initial_amount)

    # Retrieves plot
    t0 = rd.Inventory({isotope: initial_amount}, amount_unit)
    t0.plot(time, time_unit, yunits=amount_unit)

    # Fills result box
    result_box.insert(tk.END, "Plotted!")
    result_box.config(state="disabled", height=1)

    # Shows plot
    plt.title(isotope, fontsize=12)
    plt.show()

"""
This function handles the error-checking for activities.
The function handles the following errors:
   Non-number time input
   Time cannot be negative
   Non-number initial input
   Initial cannot be negative
   Isotope is stable
The function returns a bool indicating whether or not
an error occurred.
"""
def is_error(isotope, time, initial_amount, result_box):
    # Error check for a non-number time input
    try:
        time = float(time)
    except ValueError:
        result_box.insert(tk.END, "Error: Non-number time input.")
        result_box.config(state="disabled", height=1)
        return True

    # Error check for a negative time input
    if time < 0:
        result_box.insert(tk.END, "Error: Time cannot be negative.")
        result_box.config(state="disabled", height=1)
        return True

    # Error check for a non-number initial input
    try:
        initial_amount = float(initial_amount)
    except ValueError:
        result_box.insert(tk.END, "Error: Non-number initial input.")
        result_box.config(state="disabled", height=1)
        return True

    # Error check for a negative initial amount input
    if initial_amount < 0:
        result_box.insert(tk.END, "Error: Initial cannot be negative.")
        result_box.config(state="disabled", height=1)
        return True

    # Error check for stable isotope
    if math.isinf(rd.Nuclide(isotope).half_life()):
        result_box.insert(tk.END, "Isotope " + isotope + " is stable.")
        result_box.config(state="disabled", height=1)
        return True

    return False