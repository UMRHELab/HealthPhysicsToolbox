##### IMPORTS #####
import math
import shelve
import tkinter as tk
import radioactivedecay as rd
import matplotlib.pyplot as plt
from Utility.Functions.gui_utility import edit_result
from Utility.Functions.choices import get_chosen_nuclides
from Utility.Functions.files import save_file, get_user_data_path

#####################################################################################
# CALCULATIONS SECTION
#####################################################################################

"""
This function is called when the Calculate button is hit.
The function checks if the time already has an error.
If not, the function decides what calculation to
perform based on the selected calculation mode.
"""
def handle_calculation(root, mode, isotope, initial_amount, time, dates,
                       result_box, nuclide_vars, save):
    root.focus()

    # Error-check for invalid time inputs
    if dates:
        if isinstance(time, str) and time[0:5] == "Error":
            edit_result(time, result_box)
            return

    match mode:
        case "Activities":
            nuclide_activities(isotope, initial_amount, time, dates, result_box,
                               nuclide_vars)
        case "Plot":
            nuclide_plot(isotope, initial_amount, time, dates, result_box,
                         nuclide_vars, save)

"""
This function retrieves the activities
given a particular isotope, initial amount, and time.
"""
def nuclide_activities(isotope, initial_amount, time, dates, result_box, nuclide_vars):
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

    # Gets desired nuclides for plot
    nuclides = get_chosen_nuclides(nuclide_vars)

    # Fills result box
    for activity in activities:
        if activity in nuclides:
            result_box.insert(tk.END, f"{activity}, {activities[activity]:.4g}\n")
    result_box.config(state="disabled", height=len(nuclides))

"""
This function retrieves the activities plot
given a particular isotope, initial amount, and time.
"""
def nuclide_plot(isotope, initial_amount, time, dates, result_box,
                 nuclide_vars, save):
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

    # Gets desired nuclides for plot
    nuclides = get_chosen_nuclides(nuclide_vars)

    # Retrieves plot
    t0 = rd.Inventory({isotope: initial_amount}, amount_unit)
    fig, ax = t0.plot(time, time_unit, yunits=amount_unit, display=nuclides)

    # Fills result box
    result_box.insert(tk.END, "Plotted!")
    result_box.config(state="disabled", height=1)

    # Titles plot
    plt.title(isotope, fontsize=12)

    if not save:
        # Shows plot
        plt.show()
    else:
        # Saves plot
        save_file(fig, "Plot", result_box, isotope, "decay", True)

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