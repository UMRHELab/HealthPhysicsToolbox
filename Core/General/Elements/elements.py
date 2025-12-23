##### IMPORTS #####
import csv
import shelve
import pandas as pd
import tkinter as tk
from Utility.Functions.files import save_file, resource_path, get_user_data_path
from Utility.Functions.math_utility import atomic_mass_numerator, atomic_mass_denominator

#####################################################################################
# ACTIONS SECTION
#####################################################################################

"""
This function is called when the Display Info button
or Export Info button is hit.
The Atomic Mass column is converted to the desired units.
The information is then either displayed in a pop-up window
or exported to a csv file.
"""
def handle_action(root, element, export = False):
    root.focus()

    # Gets atomic mass units from user prefs
    db_path = get_user_data_path("Settings/General/Elements")
    with shelve.open(db_path) as prefs:
        num = prefs.get("am_num", "g")
        den = prefs.get("am_den", "mol")

    # Stores element information in a dictionary
    path = resource_path('Data/General Data/Periodic Table of Elements.csv')
    information = {}
    index = 0
    with open(path, 'r') as file:
        reader = csv.DictReader(file)
        for i, row in enumerate(reader):
            if row and row['Symbol'] == element:
                information = row
                index = i
                break

    if not export:
        # Create pop-up window
        popup, scroll_frame = window(element)

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
    else:
        with open(path, 'r') as file:
            reader = csv.DictReader(file)
            df = pd.DataFrame(reader)

            # Convert atomic mass to desired unit
            df.at[index, 'Atomic Mass'] = float(df.at[index, 'Atomic Mass'])
            df.at[index, 'Atomic Mass'] *= atomic_mass_numerator[num]
            df.at[index, 'Atomic Mass'] /= atomic_mass_denominator[den]

            df.rename(columns={'Atomic Mass': f'Atomic Mass ({num}/{den})'}, inplace=True)
            save_file(df.loc[[index]], "", None, element, "information")

#####################################################################################
# ACTIONS SECTION
#####################################################################################

"""
This function creates the pop-up window to display the element information.
This includes a title and making the window scrollable.
"""
def window(element):
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

    return popup, scroll_frame