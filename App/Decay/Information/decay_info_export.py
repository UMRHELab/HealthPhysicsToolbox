##### IMPORTS #####
import shelve
import platform
import tkinter as tk
from tkinter import ttk
import tkinter.font as font
from App.style import SectionFrame
from Utility.Functions.files import get_user_data_path
from Utility.Functions.math_utility import energy_units
from Core.Decay.Information.energies_export import export_data
from Utility.Functions.gui_utility import make_spacer, get_width, make_unit_dropdown
from Utility.Functions.logic_utility import get_item, get_interactions, get_threshold
from Utility.Functions.gui_utility import interaction_checkbox, make_title_frame, basic_label

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

    # Creates font for result label and energy entry
    monospace_font = font.Font(family="Menlo", size=12)

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
                                style="Maize.TButton", padding=(0,0),
                                command=lambda: default_sort())
    default_button.config(width=get_width(["Default"]))
    default_button.pack(pady=(20,0))

    # Horizontal frame for column settings
    column_side_frame = tk.Frame(inner_sort_frame, bg="#F2F2F2")
    column_side_frame.pack(pady=(20,0))

    # Column label
    column_label = ttk.Label(column_side_frame, text="Column:", style="Black.TLabel")
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
    order_label = ttk.Label(order_side_frame, text="Order:", style="Black.TLabel")
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

    # Frame for setting thresholds
    threshold_frame = SectionFrame(root, title="Set Thresholds")
    threshold_frame.pack()
    inner_threshold_frame = threshold_frame.get_inner_frame()

    # Stores whether to apply yield threshold
    var_yield = tk.IntVar()
    var_yield.set(0)

    # Creates checkbox for using yield threshold
    yield_threshold = ttk.Checkbutton(inner_threshold_frame, text="Use Yield Threshold", variable=var_yield,
                                      style="Maize.TCheckbutton", command=lambda: root.focus())
    yield_threshold.pack(pady=(10,5))

    # Stores whether to apply energy threshold
    var_energy = tk.IntVar()
    var_energy.set(0)

    # Creates checkbox for using energy threshold
    energy_threshold = ttk.Checkbutton(inner_threshold_frame, text="Use Energy Threshold", variable=var_energy,
                                       style="Maize.TCheckbutton", command=lambda: root.focus())
    energy_threshold.pack(pady=(0,5))

    # Input box width
    entry_width = 10 if platform.system() == "Windows" else 12

    # Yield label
    basic_label(inner_threshold_frame, "Yield:")

    # Horizontal frame for yield threshold settings
    yield_side_frame = tk.Frame(inner_threshold_frame, bg="#F2F2F2")
    yield_side_frame.pack(pady=(5,10))

    # Min label
    yield_min_label = ttk.Label(yield_side_frame, text="Min:", style="Black.TLabel")
    yield_min_label.pack(side='left', padx=5)

    # Min entry
    yield_min_entry = tk.Entry(yield_side_frame, width=entry_width, insertbackground="black",
                               background="white", foreground="black", borderwidth=3, bd=3,
                               highlightthickness=0, relief='solid', font=monospace_font)
    yield_min_entry.pack(side='left', padx=5)

    # Max label
    yield_max_label = ttk.Label(yield_side_frame, text="Max:", style="Black.TLabel")
    yield_max_label.pack(side='left', padx=5)

    # Max entry
    yield_max_entry = tk.Entry(yield_side_frame, width=entry_width, insertbackground="black",
                               background="white", foreground="black", borderwidth=3, bd=3,
                               highlightthickness=0, relief='solid', font=monospace_font)
    yield_max_entry.pack(side='left', padx=5)

    # Energy label
    energy_label = basic_label(inner_threshold_frame, "Energy ("+energy_unit+"):")

    # Horizontal frame for energy threshold settings
    energy_side_frame = tk.Frame(inner_threshold_frame, bg="#F2F2F2")
    energy_side_frame.pack(pady=(5,10))

    # Min label
    energy_min_label = ttk.Label(energy_side_frame, text="Min:", style="Black.TLabel")
    energy_min_label.pack(side='left', padx=5)

    # Min entry
    energy_min_entry = tk.Entry(energy_side_frame, width=entry_width, insertbackground="black",
                                background="white", foreground="black", borderwidth=3, bd=3,
                                highlightthickness=0, relief='solid', font=monospace_font)
    energy_min_entry.pack(side='left', padx=5)

    # Max label
    energy_max_label = ttk.Label(energy_side_frame, text="Max:", style="Black.TLabel")
    energy_max_label.pack(side='left', padx=5)

    # Max entry
    energy_max_entry = tk.Entry(energy_side_frame, width=entry_width, insertbackground="black",
                                background="white", foreground="black", borderwidth=3, bd=3,
                                highlightthickness=0, relief='solid', font=monospace_font)
    energy_max_entry.pack(side='left', padx=5)

    # Spacer
    empty_frame3 = make_spacer(root)

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

        # Fixes energy threshold label
        energy_label.config(text="Energy ("+selection+"):")

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
                                           var_order.get(),
                                           get_threshold(var_yield.get(),
                                                         yield_min_entry.get(), True),
                                           get_threshold(var_yield.get(),
                                                         yield_max_entry.get(), False),
                                           get_threshold(var_energy.get(),
                                                         energy_min_entry.get(), True),
                                           get_threshold(var_energy.get(),
                                                         energy_max_entry.get(), False)
                                           ))
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
                   threshold_frame, empty_frame3,
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