##### IMPORTS #####
import csv
import json
import math
import shelve
from tkinter import IntVar
import radioactivedecay as rd
from Utility.Functions.files import resource_path, get_user_data_path

# Choices using an element or a material
element_choices = ["Common Elements", "All Elements"]
material_choices = ["Common Materials", "All Materials"]

#####################################################################################
# INTERACTING MEDIUM SECTION
#####################################################################################

"""
This function returns the list of items (elements/materials)
in the selected category.
If the category is either All Elements or All Materials,
the choices are read from a Data file.
Otherwise, the choices are retrieved from the user's
shelve data.
If the category is either Custom Elements or Custom Materials,
a default list is read from a Data file which is used
if no user shelve data is stored.
If the category is Custom Materials, the default list is empty.
"""
def get_choices(category, module, particle):
    choices = []

    if module == "Deposition" and particle == "Photons":
        particle = "Alphas"

    if category == "All Materials":
        # Obtains list of items from csv file
        db_path = resource_path('Data/General Data/Density/Materials.csv')
        read_choices(choices, db_path)
        if particle == "Alphas":
            return [choice for choice in choices if "Plutonium" not in choice]
        return choices

    if category == "All Elements":
        # Obtains list of items from csv file
        data = "ICRP Coefficients" if module == "Dose" else "NIST Coefficients"
        db_path = resource_path('Data/' + data + '/' + particle + '/Elements.csv')
        if module == "Decay":
            db_path = resource_path('Data/Radioactive Decay/Elements.csv')
        if module == "General":
            read_pt_choices(choices)
            choices.sort()
        else:
            read_choices(choices, db_path)
        return choices

    # Obtains list of items from shelve
    db_path = get_user_data_path(category)
    with shelve.open(db_path) as prefs:
        default = []
        if category != "Custom Materials":
            # Obtains list of default items from csv file
            db_path2 = resource_path('Data/General Data/' + category + '.csv')
            read_choices(default, db_path2)
        choices = prefs.get(category, default)
        choices.sort()
        return choices

"""
This function reads the list of items (elements/materials)
from a csv data file.
"""
def read_choices(choices, path):
    with open(path, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row and row[0] != 'Name':
                choices.append(row[0])

"""
This function reads the list of elements
from the Periodic Table.
"""
def read_pt_choices(choices):
    path = resource_path('Data/General Data/Periodic Table of Elements.csv')
    with open(path, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row and row[2] != 'Symbol':
                choices.append(row[2])

#####################################################################################
# ISOTOPE SECTION
#####################################################################################

"""
Gets all isotopes of an element.
"""
def get_isotopes(element):
    db_path = resource_path("Data/Radioactive Decay/Isotopes.json")
    with open(db_path, "r") as f:
        isotopes = json.load(f)
    return isotopes.get(element, [])

"""
Gets all isotopes of an element for a particular ICRP publication.
"""
def get_icrp_isotopes(element, publication):
    db_path = resource_path("Data/ICRP Coefficients/"+publication+"/Isotopes.json")
    with open(db_path, "r") as f:
        isotopes = json.load(f)
    return isotopes.get(element, [])

"""
Gets all successors of an isotope in a decay chain.
"""
def get_successors(isotope):
    if not isotope or math.isinf(rd.Nuclide(isotope).half_life()):
        return []
    t0 = rd.Inventory({isotope: 0})
    t1 = t0.decay(0)
    activities_og = t1.activities()
    activities = []
    for activity in activities_og:
        activities.append(str(activity))
    return activities

"""
Makes an IntVar for each successor of an isotope.
"""
def get_nuclide_vars(isotope):
    # Gets successors of isotope
    successors = get_successors(isotope)

    # Makes an IntVar for each successor
    nuclide_vars = {}
    for successor in successors:
        new_var = IntVar()
        new_var.set(1)
        nuclide_vars[successor] = new_var

    return nuclide_vars

"""
Gets the selected nuclides from the nuclide variables.
"""
def get_chosen_nuclides(nuclide_vars) -> list[str]:
    nuclides = []
    for nuc, var in nuclide_vars.items():
        if var.get():
            nuclides.append(nuc)

    return nuclides

#####################################################################################
# COLUMNS SECTION
#####################################################################################

"""
This function reads the list of columns
from the Periodic Table.
"""
def read_pt_columns(choices):
    path = resource_path('Data/General Data/Periodic Table Columns.csv')
    with open(path, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row and row[0] != 'Column' and row[0] != 'Symbol':
                choices.append(row[0])

"""
This function reads the list of columns for dose coefficients
from a csv data file.
"""
def read_dose_columns(choices, publication):
    path = resource_path(f'Data/ICRP Coefficients/{publication}/Columns.csv')
    with open(path, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row and row[0] != 'Nuclide' and row[0] != 'Type':
                choices.append(row[0])