##### IMPORTS #####
import io
import csv
import shelve
import tkinter as tk
from Utility.Functions.choices import get_choices
from Utility.Functions.files import get_user_data_path
from Utility.Functions.math_utility import density_numerator, density_denominator

"""
This function is called when the Add Material button is hit.
The function handles the following errors:
   No material name provided
   Maximum material name length exceeded
   No density provided
   Non-number density input
   Density must be positive
   No element weights provided
   Each line must have a weight, a comma, and an element
   Non-number weight input
   Weights must be in range (0, 1]
   Invalid element
   Element weights do not sum to 1; select normalize to fix
If there are no errors, the element weights input is cleaned up.
Then, the material name is added to the list of Custom Materials in shelve.
The material data is also stored in shelve, with the density converted to g/cm^3.
Finally, the input boxes are cleared.
"""
def add_custom(root, name_box, density_box, weights_box, error_label, normalize,
               d_num, d_den):
    root.focus()
    name = name_box.get()

    # Error check for no material name
    if name == "":
        error_label.config(style="Error.TLabel", text="Error: No material name provided.")
        return

    # Error check for lengthy material name
    if len(name) > 50:
        error_label.config(style="Error.TLabel", text="Error: Maximum material name length exceeded.")
        return

    density = density_box.get()

    if density == "":
        error_label.config(style="Error.TLabel", text="Error: No density provided.")
        return

    # Error check for a non-number density input
    try:
        _ = float(density)
    except ValueError:
        error_label.config(style="Error.TLabel", text="Error: Non-number density input.")
        return

    if float(density) <= 0:
        error_label.config(style="Error.TLabel", text="Error: Density must be positive.")
        return

    weights = weights_box.get("1.0", "end-1c")

    cleaned_input = '\n'.join(
        ','.join(field.strip() for field in line.split(','))
        for line in weights.strip().splitlines()
    )

    # Error check for no weights
    if cleaned_input == "":
        error_label.config(style="Error.TLabel", text="Error: No element weights provided.")
        return

    csv_data = f'"Weight","Element"\n{cleaned_input}'

    # Create file-like object from the stored string
    csv_file_like = io.StringIO(csv_data)

    reader = csv.reader(csv_file_like)
    elements = get_choices("All Elements", "", "Alphas")
    weights_sum = 0

    for row in reader:
        # Error check for bad rows
        if not (len(row) == 2):
            error_label.config(style="Error.TLabel",
                               text="Error: Each line must have a weight, a comma, and an element.")
            return

        # Error check for a non-number weight input
        try:
            if row[0] != "Weight":
                weights_sum += float(row[0])
        except ValueError:
            error_label.config(style="Error.TLabel", text="Error: Non-number weight input.")
            return

        # Error check for an element weight outside (0, 1]
        if row[0] != "Weight" and (float(row[0]) > 1 or float(row[0]) <= 0):
            error_label.config(style="Error.TLabel", text="Error: Weights must be in range (0, 1].")
            return

        # Error check for an invalid element
        if row[1] != "Element" and not row[1] in elements:
            error_label.config(style="Error.TLabel", text=f"Error: Invalid element: {row[1]}.")
            return

    # Error check for weights that do not sum to 1
    if weights_sum != 1 and normalize == 0:
        error_label.config(style="Error.TLabel",
                           text="Error: Element weights do not sum to 1; select normalize to fix.")
        return

    csv_data2 = ""

    # Create file-like object from the stored string
    csv_file_like2 = io.StringIO(csv_data)

    # Cleans up input
    reader2 = csv.reader(csv_file_like2)
    for row in reader2:
        row[0] = row[0].strip()
        if row[0] != "Weight":
            row[0] = str(float(row[0]) / weights_sum)
        csv_data2 += f"{row[0].strip()},"
        csv_data2 += f"{row[1].strip()}\n"
    csv_data = csv_data2.rstrip("\n")

    error_label.config(style="Success.TLabel", text="Material added!")

    # Add material name to list of Custom Materials
    db_path = get_user_data_path('Custom Materials')
    with shelve.open(db_path) as prefs:
        choices = prefs.get("Custom Materials", [])
        if not name in choices:
            choices.append(name)
        prefs["Custom Materials"] = choices

    # Save material data to shelve
    db_path2 = get_user_data_path(f'Custom Materials/_{name}')
    with shelve.open(db_path2) as db:
        # Store name
        db[name] = csv_data

        # Convert density to g/cm^3 before storing
        db[f'{name}_Density'] = str(float(density) * density_denominator[d_den] / density_numerator[d_num])

    # Clear input boxes
    name_box.delete(0, tk.END)
    weights_box.delete("1.0", "end")
    density_box.delete(0, tk.END)