##### IMPORTS #####
import io
import shelve
import pandas as pd
from PIL import Image
from collections import deque
import radioactivedecay as rd
import matplotlib.pyplot as plt
from Utility.Functions.files import save_file
from Utility.Functions.gui_utility import edit_result
from Utility.Functions.files import get_user_data_path

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
The function decides what calculation to perform
based on the selected calculation mode.
"""
def handle_calculation(root, mode, isotope, result_box, save):
    root.focus()
    match mode:
        case "Decay Scheme (Plot)":
            nuclide_decay_scheme(isotope, result_box, save)
        case "Decay Scheme (Tabular)":
            nuclide_decay_scheme_tabular(isotope, result_box)
        case "Half Life":
            nuclide_half_life(isotope, result_box)

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