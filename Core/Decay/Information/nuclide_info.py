##### IMPORTS #####
import io
import math
import json
import shelve
import pandas as pd
import tkinter as tk
from PIL import Image
from collections import deque
import radioactivedecay as rd
import matplotlib.pyplot as plt
from Utility.Functions.plot import configure_plot
from Utility.Functions.math_utility import energy_units
from Utility.Functions.gui_utility import edit_result, window, no_selection
from Core.Decay.Information.energies_dataframe import create_energies_dataframe
from Utility.Functions.files import save_file, get_user_data_path, resource_path

#####################################################################################
# UNITS SECTION
#####################################################################################

# Unit choices
half_life_units = ['μs', 'ms', 's', 'm', 'h', 'd', 'y', 'readable']

#####################################################################################
# CALCULATIONS SECTION
#####################################################################################

"""
This function is called when the Calculate button is hit.
The function handles the following error:
   No selected element
The function decides what calculation to perform
based on the selected calculation mode.
"""
def handle_calculation(root, mode, isotope, result_box, save):
    root.focus()

    # Error-check for no selected element
    if isotope == "":
        edit_result(no_selection, result_box)
        return

    match mode:
        case "Decay Scheme (Plot)":
            nuclide_decay_scheme(isotope, result_box, save)
        case "Decay Scheme (Tabular)":
            nuclide_decay_scheme_tabular(isotope, result_box)
        case "Half Life":
            nuclide_half_life(isotope, result_box)
        case "Energies":
            nuclide_energies(isotope, result_box)
        case "Beta Spectrum":
            nuclide_beta_spectrum(isotope, result_box, save)
        case "Auger Electron Spectrum":
            nuclide_auger_electron_spectrum(isotope, result_box, save)
        case "Neutron Spectrum":
            nuclide_neutron_spectrum(isotope, result_box, save)

"""
This function retrieves the decay scheme plot
given a particular isotope.
"""
def nuclide_decay_scheme(isotope, result_box, save):
    nuc = rd.Nuclide(isotope)
    fig, ax = nuc.plot()
    if not save:
        fig.tight_layout()
        buf = io.BytesIO()
        fig.savefig(buf, format="PNG", bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        img = Image.open(buf)
        edit_result("Plot opened!", result_box)
        img.show()
    else:
        save_file(fig, "Plot", result_box, isotope, "decay_scheme", True)

"""
This function details the decay scheme of a given
particular isotope in tabular format.
"""
def nuclide_decay_scheme_tabular(isotope, result_box):
    # Sets up columns for dataframe
    cols = ["Parent", "Progeny", "Branching Fractions", "Decay Modes"]

    # Sets up queue
    q = deque()
    q.append(isotope)
    index = 0

    # Sets up set (prevents duplicates)
    s = {isotope}

    # Sets up dataframe
    df = pd.DataFrame(columns=cols)

    # Recurses on children until reaching stable isotopes
    while q:
        x = q.popleft()
        nuc = rd.Nuclide(x)

        progeny = nuc.progeny()
        branching_fractions = nuc.branching_fractions()
        decay_modes = nuc.decay_modes()

        for num, child in enumerate(progeny):
            parent = x if num == 0 else ""
            df.loc[index] = {"Parent": parent,
                             "Progeny": progeny[num],
                             "Branching Fractions": branching_fractions[num],
                             "Decay Modes": decay_modes[num]
                             }
            index += 1
            if not child in s:
                q.append(child)
                s.add(child)
        if len(progeny) == 0:
            df.loc[index] = {"Parent": x,
                             "Progeny": "None",
                             "Branching Fractions": "N/A",
                             "Decay Modes": "N/A"
                             }
            index += 1

    save_file(df, "Data", result_box, isotope, "decay_scheme", True)

"""
This function retrieves the half-life
given a particular isotope.
"""
def nuclide_half_life(isotope, result_box):
    # Gets half-life unit from user prefs
    db_path = get_user_data_path("Settings/Decay/Information")
    with shelve.open(db_path) as prefs:
        unit = prefs.get("hl_unit", "s")

    nuc = rd.Nuclide(isotope)
    result = nuc.half_life(unit)
    if unit == "readable":
        edit_result(result, result_box)
    else:
        edit_result(f"{result} {unit}", result_box)

"""
This function creates a pop-up window displaying
the energies of the provided isotope.
The function handles the following errors:
   Isotope is stable
   No radiation types selected
   Non-number filter input
   Filter input must be in range [0, 100]
   No data for isotope
"""
def nuclide_energies(isotope, result_box):
    # List of neutron irrelevant radiation types
    neutron_irrelevant_types = [
        "Gamma Ray", "Annihilation Photon",
        "X-Ray", "Beta- Particle", "Beta+ Particle",
        "Internal Conversion Electron", "Auger Electron",
        "Alpha Particle"
    ]

    # Gets radiation types, filter percentage, and energy unit from user prefs
    db_path = get_user_data_path("Settings/Decay/Information")
    with shelve.open(db_path) as prefs:
        rad_types = prefs.get("rad_types", [rad_type for rad_type in neutron_irrelevant_types])
        filter_percentage = prefs.get("filter_percentage", "100")
        energy_unit = prefs.get("energy_unit", "MeV")

    # Error-check for isotope is stable
    if math.isinf(rd.Nuclide(isotope).half_life('s')):
        edit_result("Error: "+isotope+" is stable.", result_box)
        return

    # Error-check for no radiation types selected
    if len(rad_types) == 0:
        edit_result("Error: No radiations selected.", result_box)
        return

    # Error-check for a non-number filter input
    try:
        filter_percentage = float(filter_percentage)
    except ValueError:
        edit_result("Error: Non-number filter input.", result_box)
        return

    # Error-check for filter input outside of range [0, 100]
    if filter_percentage < 0 or filter_percentage > 100:
        edit_result("Error: Filter must be [0, 100].", result_box)
        return

    # Create pop-up window
    popup, scroll_frame = window(isotope+" Energies", "600x600")

    # Gets element
    element = isotope.split('-')[0]

    # Creates dataframe
    df = create_energies_dataframe(element, isotope, result_box, True)
    if df is None:
        return

    # Header
    row = tk.Frame(scroll_frame)
    row.pack(fill="x", padx=10)
    tk.Label(row, text="Radiation Type", width=30, anchor="w", font=("Arial", 10, "bold")).pack(side="left")
    tk.Label(row, text="Yield", width=20, anchor="w").pack(side="left")
    tk.Label(row, text=f"Energy ({energy_unit})", anchor="w").pack(side="left")

    # Populate fields
    for _, row in df.iterrows():
        type_val = row["Radiation Type"]
        yield_val = row["Yield"]
        energy = row[f"Energy ({energy_unit})"]
        row = tk.Frame(scroll_frame)
        row.pack(fill="x", padx=10)

        tk.Label(row, text=f"{type_val}:", width=30, anchor="w", font=("Arial", 10, "bold")).pack(side="left")
        tk.Label(row, text=str(yield_val), width=20, anchor="w").pack(side="left")
        tk.Label(row, text=str(energy), anchor="w").pack(side="left")

    tk.Button(popup, text="Close", command=popup.destroy).pack(pady=10)

"""
This function plots the beta spectrum for the given isotope.
The function handles the following error:
   No data for isotope
"""
def nuclide_beta_spectrum(isotope, result_box, save):
    # Gets energy unit from user prefs
    db_path = get_user_data_path("Settings/Decay/Information")
    with shelve.open(db_path) as prefs:
        energy_unit = prefs.get("energy_unit", "MeV")

    # Gets element
    element = isotope.split('-')[0]

    # Retrieves data and creates dataframe
    db_path = resource_path('Data/Radioactive Decay/Spectra/Betas/' + element + '.json')
    try:
        with open(db_path, 'r') as file:
            # Retrieves data
            data = json.load(file).get(isotope, -1)

            # Error-check for missing data
            if data == -1:
                edit_result("No data for " + isotope + ".", result_box)
                return

            df = pd.DataFrame(data)
    except FileNotFoundError:
        edit_result("No data for " + isotope + ".", result_box)
        return

    # Fixes dataframe
    df["energy_MeV"] = df["energy_MeV"].astype(float)
    df["electrons"] = df["electrons"].astype(float)

    # Sets up columns for dataframe
    energy_col = "Energy (" + energy_unit + ")"
    df.rename(columns={'energy_MeV': energy_col,
                       'electrons' : 'Electrons'},
              inplace=True)

    # Converts energy column to desired energy unit
    df[energy_col] /= energy_units[energy_unit]

    configure_plot(None, df, energy_col, "Electrons", "Beta Spectrum")
    if not save:
        edit_result("Plot opened!", result_box)
        plt.show()
    else:
        save_file(plt, "Plot", result_box, isotope, "beta", True)

"""
This function plots the auger electron spectrum for the given isotope.
The function handles the following error:
   No data for isotope
"""
def nuclide_auger_electron_spectrum(isotope, result_box, save):
    # Gets energy unit from user prefs
    db_path = get_user_data_path("Settings/Decay/Information")
    with shelve.open(db_path) as prefs:
        energy_unit = prefs.get("energy_unit", "MeV")

    # Gets element
    element = isotope.split('-')[0]

    # Retrieves data and creates dataframe
    try:
        db_path = resource_path('Data/Radioactive Decay/Spectra/Auger/' + element + '.json')
        with open(db_path, 'r') as file:
            # Retrieves data
            data = json.load(file).get(isotope, -1)

            # Error-check for missing data
            if data == -1:
                edit_result("No data for " + isotope + ".", result_box)
                return

            df = pd.DataFrame(data["records"])
    except FileNotFoundError:
        edit_result("No data for " + isotope + ".", result_box)
        return

    # Fixes dataframe
    df["energy_eV"] = df["energy_eV"].astype(float)
    df["yield"] = df["yield"].astype(float)

    # Sets up columns for dataframe
    energy_col = "Energy (" + energy_unit + ")"
    df.drop(columns=['orbital_transition'], inplace=True)
    df.rename(columns={'energy_eV': energy_col,
                       'yield' : 'Yield'},
              inplace=True)

    # Converts energy column to desired energy unit
    eV_to_MeV = 1000 ** 2
    df[energy_col] /= (energy_units[energy_unit] * eV_to_MeV)

    configure_plot(None, df, energy_col, "Yield", "Auger Electron Spectrum")
    if not save:
        edit_result("Plot opened!", result_box)
        plt.show()
    else:
        save_file(plt, "Plot", result_box, isotope, "auger", True)

"""
This function plots the neutron spectrum for the given isotope.
The function handles the following error:
   No data for isotope
"""
def nuclide_neutron_spectrum(isotope, result_box, save):
    # Gets energy unit from user prefs
    db_path = get_user_data_path("Settings/Decay/Information")
    with shelve.open(db_path) as prefs:
        energy_unit = prefs.get("energy_unit", "MeV")

    # Gets element
    element = isotope.split('-')[0]

    # Retrieves data and creates dataframe
    db_path = resource_path('Data/Radioactive Decay/Spectra/Neutrons/' + element + '.json')
    try:
        with open(db_path, 'r') as file:
            # Retrieves data
            data = json.load(file).get(isotope, -1)

            # Error-check for missing data
            if data == -1:
                edit_result("No data for " + isotope + ".", result_box)
                return

            df = pd.DataFrame(data["records"])
    except FileNotFoundError:
        edit_result("No data for " + isotope + ".", result_box)
        return

    # Fixes dataframe
    df["floor_energy_MeV"] = df["floor_energy_MeV"].astype(float)
    df["ceiling_energy_MeV"] = df["ceiling_energy_MeV"].astype(float)
    df["neutrons"] = df["neutrons"].astype(float)

    # Converts energy column to desired energy unit
    df["floor_energy_MeV"] /= energy_units[energy_unit]
    df["ceiling_energy_MeV"] /= energy_units[energy_unit]

    # Compute bin edges and counts for step plot
    edges = df["floor_energy_MeV"].tolist() + [df["ceiling_energy_MeV"].iloc[-1]]
    counts = df["neutrons"].tolist()
    counts.append(counts[-1])

    # Configures plot
    plt.figure(figsize=(8,5))
    plt.step(edges, counts, where='post', color='blue')
    plt.fill_between(edges, counts, step='post', alpha=0.3, color='blue')
    plt.xlabel("Energy (MeV)")
    plt.ylabel("Neutrons")
    plt.title("Neutron Spectrum")
    plt.grid(True)

    if not save:
        edit_result("Plot opened!", result_box)
        plt.show()
    else:
        save_file(plt, "Plot", result_box, isotope, "neutron", True)