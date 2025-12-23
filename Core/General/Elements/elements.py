##### IMPORTS #####
import csv
import shelve
import tkinter as tk
from Utility.Functions.files import resource_path
from Utility.Functions.files import get_user_data_path
from Utility.Functions.math_utility import atomic_mass_numerator, atomic_mass_denominator

#####################################################################################
# CALCULATIONS SECTION
#####################################################################################

"""
This function is called when the Calculate button is hit.
The function decides what calculation to perform
based on the selected calculation mode.
If the calculation mode is Atomic Mass, the result is
converted to the desired units.
"""
def handle_calculation(root, element):
    root.focus()

    popup = tk.Toplevel()
    popup.title(element+" Information")
    popup.geometry("400x600")
    popup.transient()

    # Scrollable frame
    canvas = tk.Canvas(popup)
    scrollbar = tk.Scrollbar(popup, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas)

    scroll_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0,0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Gets atomic mass units from user prefs
    db_path = get_user_data_path("Settings/General/Elements")
    with shelve.open(db_path) as prefs:
        num = prefs.get("am_num", "g")
        den = prefs.get("am_den", "mol")

    path = resource_path('Data/General Data/Periodic Table of Elements.csv')
    information = {}
    with open(path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row and row['Symbol'] == element:
                information = row
                break

    # Convert atomic mass to desired unit
    information["Atomic Mass"] = float(information["Atomic Mass"])
    information["Atomic Mass"] *= atomic_mass_numerator[num]
    information["Atomic Mass"] /= atomic_mass_denominator[den]
    information["Atomic Mass"] = f"{information["Atomic Mass"]} {num}/{den}"

    # Populate fields
    for key, value in information.items():
        row = tk.Frame(scroll_frame)
        row.pack(fill="x", padx=10)

        tk.Label(row, text=f"{key}:", width=20, anchor="w", font=("Arial", 10, "bold")).pack(side="left")
        tk.Label(row, text=str(value), anchor="w").pack(side="left")

    tk.Button(popup, text="Close", command=popup.destroy).pack(pady=10)