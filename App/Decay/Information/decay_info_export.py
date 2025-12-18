##### IMPORTS #####
import shelve
import tkinter as tk
from tkinter import ttk
from App.style import SectionFrame
from Utility.Functions.files import get_user_data_path
from Utility.Functions.math_utility import energy_units
from Core.Decay.Information.energies_export import export_data
from Utility.Functions.logic_utility import get_item, get_interactions
from Utility.Functions.gui_utility import make_unit_dropdown, interaction_checkbox
from Utility.Functions.gui_utility import make_spacer, get_width, make_title_frame

# For global access to nodes on decay information export screen
export_list = []

#####################################################################################
# MENU SECTION
#####################################################################################

"""
This function sets up the decay information export screen.
The following sections and widgets are created:
   Module Title (Decay Information)
   Export Options section
   Back button
This function contains all of the logic involving these widgets'
behaviors.
The sections and widgets are stored in export_list so they can be
accessed later by clear_export.
"""
def decay_info_export(root, category, mode, common_el, element, isotope):
    global export_list

    # Gets energy unit from user prefs
    db_path = get_user_data_path("Settings/Decay/Information")
    with shelve.open(db_path) as prefs:
        energy_unit = prefs.get("energy_unit", "MeV")

    # Makes title frame
    title_frame = make_title_frame(root, "Decay Information", "Decay/Information")

    # Frame for radiation types
    radiation_types_frame = SectionFrame(root, title="Select Radiation Types")
    radiation_types_frame.pack()
    inner_radiation_types_frame = radiation_types_frame.get_inner_frame()
    inner_radiation_types_frame.config(pady=10)

    # Logic for when a radiation type is selected
    on_select = lambda: root.focus()

    # List of radiation types
    rad_types = [
        "Gamma Ray",                      "Prompt Gamma Ray",
        "Delayed Gamma Ray",              "Annihilation Photon",
        "X-Ray",                          "Beta- Particle",
        "Delayed Beta Particle",          "Beta+ Particle",
        "Internal Conversion Electron",   "Auger Electron",
        "Alpha Particle",                 "Alpha Recoil Nucleus",
        "Fission Fragment",               "Neutron",
    ]

    # Variables for each radiation type
    rad_type_vars = [tk.IntVar(value=1) for _ in range(len(rad_types))]

    # Frame for radiation type checkboxes
    checks = tk.Frame(inner_radiation_types_frame, bg="#F2F2F2")
    checks.pack()

    # Checkboxes for each radiation type
    for index, rad_type in enumerate(rad_types):
        interaction_checkbox(checks, rad_type_vars[index], rad_type, on_select)

    # Spacer
    empty_frame1 = make_spacer(root)

    # Frame for sorting exported data
    sort_frame = SectionFrame(root, title="Sort Exported Data")
    sort_frame.pack()
    inner_sort_frame = sort_frame.get_inner_frame()

    # Sets back to default sort
    def default_sort():
        root.focus()
        var_column.set("Radiation Type")
        var_order.set("Ascending")

    # Creates button to set sort to default sort
    default_button = ttk.Button(inner_sort_frame, text="Default",
                                style="Maize.TButton", padding=(2,0),
                                command=lambda: default_sort())
    default_button.config(width=get_width(["Back"]))
    default_button.pack(pady=(20,0))

    # Horizontal frame for column settings
    column_side_frame = tk.Frame(inner_sort_frame, bg="#F2F2F2")
    column_side_frame.pack(pady=(20,0))

    # Column label
    column_label = ttk.Label(column_side_frame, text="Column:",
                             style="Black.TLabel")
    column_label.pack(side='left', padx=5)

    # Column variable
    column = "Radiation Type"

    # Stores column and sets default
    var_column = tk.StringVar(root)
    var_column.set(column)

    # Logic for when a column is selected
    def select_column(event):
        nonlocal column
        event.widget.selection_clear()

        # Update column variable
        column = var_column.get()

        root.focus()

    # Creates dropdown menu for columns
    column_choices = ["Radiation Type",
                      "Yield",
                      "Energy"]
    _ = make_unit_dropdown(column_side_frame, var_column, column_choices, select_column)

    # Horizontal frame for order settings
    order_side_frame = tk.Frame(inner_sort_frame, bg="#F2F2F2")
    order_side_frame.pack(pady=(20,20))

    # Order label
    order_label = ttk.Label(order_side_frame, text="Order:",
                             style="Black.TLabel")
    order_label.pack(side='left', padx=5)

    # Order variable
    order = "Ascending"

    # Stores order and sets default
    var_order = tk.StringVar(root)
    var_order.set(order)

    # Logic for when an order is selected
    def select_order(event):
        nonlocal order
        event.widget.selection_clear()

        # Update order variable
        order = var_order.get()

        root.focus()

    # Creates dropdown menu for orders
    order_choices = ["Ascending",
                     "Descending"]
    _ = make_unit_dropdown(order_side_frame, var_order, order_choices, select_order)

    # Spacer
    empty_frame2 = make_spacer(root)

    # Frame for options
    options_frame = SectionFrame(root, title="Export Options")
    options_frame.pack()
    inner_options_frame = options_frame.get_inner_frame()

    # Horizontal frame for unit settings
    unit_side_frame = tk.Frame(inner_options_frame, bg="#F2F2F2")
    unit_side_frame.pack(pady=(20,0))

    # Unit label
    unit_label = ttk.Label(unit_side_frame, text="Energy Unit:",
                           style="Black.TLabel")
    unit_label.pack(side='left', padx=5)

    # Logic for when an energy unit is selected
    def on_select_unit(event):
        event.widget.selection_clear()
        root.focus()
        selection = event.widget.get()
        with shelve.open(db_path) as shelve_prefs:
            shelve_prefs["energy_unit"] = selection

    # Stores energy unit and sets default
    var_unit = tk.StringVar(root)
    var_unit.set(energy_unit)

    # Creates dropdown menu for unit
    energy_choices = list(energy_units.keys())
    _ = make_unit_dropdown(unit_side_frame, var_unit, energy_choices, on_select_unit)

    # Frame for export type
    export_frame = tk.Frame(inner_options_frame, bg="#F2F2F2")
    export_frame.pack(pady=5)

    # Creates Export button
    export_button = ttk.Button(inner_options_frame, text="Export", style="Maize.TButton",
                               padding=(0,0),
                               command=lambda:
                               export_data(root,
                                           get_item(category, common_el, "", element, "", ""),
                                           set(get_interactions(rad_types, rad_type_vars)),
                                           isotope, error_label, var_column.get(),
                                           var_order.get()))
    export_button.config(width=get_width(["Export"]))
    export_button.pack(pady=(10,5))

    # Creates error label for bad input
    error_label = ttk.Label(inner_options_frame, text="", style="Error.TLabel")
    error_label.pack(pady=(5,10))

    # Creates Back button to return to decay information advanced screen
    back_button = ttk.Button(root, text="Back", style="Maize.TButton", padding=(0,0),
                             command=lambda: advanced_back(root, category, mode,
                                                           common_el, element, isotope))
    back_button.config(width=get_width(["Back"]))
    back_button.pack(pady=5)

    # Stores nodes into global list
    export_list = [title_frame,
                   radiation_types_frame, empty_frame1,
                   sort_frame, empty_frame2,
                   options_frame, back_button]

#####################################################################################
# NAVIGATION SECTION
#####################################################################################

"""
This function clears the decay information export screen
in preparation for opening a different screen.
"""
def clear_export():
    global export_list

    # Clears decay information export screen
    for node in export_list:
        node.destroy()
    export_list.clear()

"""
This function transitions from the decay information export screen
to the decay information advanced screen by first clearing the
decay information export screen and then creating the
decay information advanced screen.
It is called when the Back button is hit.
"""
def advanced_back(root, category, mode, common_el, element, isotope):
    from App.Decay.Information.decay_info_advanced import decay_info_advanced

    clear_export()
    decay_info_advanced(root, category, mode, common_el, element, isotope)