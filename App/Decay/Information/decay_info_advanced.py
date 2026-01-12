##### IMPORTS #####
import shelve
import platform
import tkinter as tk
from tkinter import ttk
import tkinter.font as font
from App.style import SectionFrame
from App.scroll import scroll_to_top
from Utility.Functions.choices import get_choices
from Utility.Functions.math_utility import energy_units
from Utility.Functions.logic_utility import get_interactions
from Core.Decay.Information.nuclide_info import half_life_units
from App.Decay.Information.decay_info_export import decay_info_export
from Utility.Functions.files import get_user_data_path, resource_path, open_file
from Utility.Functions.gui_utility import (
    basic_label,
    make_back_button,
    interaction_checkbox,
    make_spacer, get_width,
    make_title_frame, make_vertical_frame,
    make_dropdown, make_unit_dropdown, make_action_dropdown
)

# For global access to nodes on decay information advanced screen
advanced_list = []

#####################################################################################
# MENU SECTION
#####################################################################################

"""
This function sets up the decay information advanced screen.
The following sections and widgets are created:
   Module Title (Decay Information)
   Customize Common Elements section
   Select Radiation Types section (if Calculation Mode is Energies)
   Sort Data section (if Calculation Mode is Energies)
   Set Filter section (if Calculation Mode is Energies)
   Select Units section
   Export button
   References button
   Help button
   Back button
This function contains all of the logic involving these widgets'
behaviors.
The sections and widgets are stored in advanced_list so they can be
accessed later by clear_advanced.
"""
def decay_info_advanced(root, category, mode, common_el, element, isotope):
    global advanced_list

    # List of radiation types
    rad_types = [
        "Gamma Ray", "Prompt Gamma Ray",
        "Delayed Gamma Ray", "Annihilation Photon",
        "X-Ray", "Beta- Particle",
        "Delayed Beta Particle", "Beta+ Particle",
        "Internal Conversion Electron", "Auger Electron",
        "Alpha Particle", "Alpha Recoil Nucleus",
        "Fission Fragment", "Neutron",
    ]

    # List of neutron relevant radiation types
    neutron_relevant_types = [
        "Prompt Gamma Ray",
        "Delayed Gamma Ray",
        "Delayed Beta Particle",
        "Alpha Recoil Nucleus",
        "Fission Fragment",
        "Neutron",
    ]

    # Gets half-life unit, energy unit, radiation types, column, order, filter type,
    # filter direction, and filter percentage from user prefs
    db_path = get_user_data_path("Settings/Decay/Information")
    with shelve.open(db_path) as prefs:
        half_life_unit = prefs.get("hl_unit", "s")
        energy_unit = prefs.get("energy_unit", "MeV")
        selected_rad_types = prefs.get("rad_types", [rad_type for rad_type in rad_types
                                                     if rad_type not in neutron_relevant_types])
        sort_column = prefs.get("column", "Radiation Type")
        sort_order = prefs.get("order", "Ascending")
        filter_type = prefs.get("filter_type", "Yield")
        filter_dir = prefs.get("filter_dir", "Top")
        filter_percentage = prefs.get("filter_percentage", "100")

    # Makes title frame
    title_frame = make_title_frame(root, "Decay Information", "Decay/Information")

    # Gets common and non-common elements
    elements = get_choices("All Elements", "Shielding", "Photons")
    common = get_choices("Common Elements", "Shielding", "Photons")
    non_common = [element for element in elements if element not in common]

    # Frame for add/remove settings
    a_r_frame = SectionFrame(root, title="Customize Common Elements")
    a_r_frame.pack()
    inner_a_r_frame = a_r_frame.get_inner_frame()

    # Action button
    a_r_button = [ttk.Button()]

    # Simplifies calls to make_vertical_frame
    def make_v_frame():
        to_custom = lambda: root.focus()
        return make_vertical_frame(root, inner_a_r_frame, var_action.get(),
                                   "Common Elements", non_common, common,
                                   [], [], [], a_r_button, to_custom)

    # Logic for when an action is selected
    def on_select_action(event):
        nonlocal vertical_frame
        event.widget.selection_clear()
        root.focus()
        vertical_frame.destroy()
        vertical_frame = make_v_frame()

    # Frame for action selection
    action_frame = tk.Frame(inner_a_r_frame, bg="#F2F2F2")
    action_frame.pack(pady=(15,5))

    # Action label
    basic_label(action_frame, "Action:")

    # Stores action and sets default
    var_action = tk.StringVar(root)
    var_action.set("Add")

    # Creates dropdown menu for action
    _ = make_action_dropdown(action_frame, var_action, on_select_action)

    # Frame for specific add/remove settings
    vertical_frame = make_v_frame()

    # Spacer
    empty_frame1 = make_spacer(root)

    # Assignment
    radiation_types_frame = tk.Frame()
    sort_frame = tk.Frame()
    filter_frame = tk.Frame()
    empty_frame2 = tk.Frame()
    empty_frame3 = tk.Frame()
    empty_frame4 = tk.Frame()

    if mode == "Energies":
        # Creates font for result label and energy entry
        monospace_font = font.Font(family="Menlo", size=12)

        # Frame for radiation types
        radiation_types_frame = SectionFrame(root, title="Select Radiation Types")
        radiation_types_frame.pack()
        inner_radiation_types_frame = radiation_types_frame.get_inner_frame()
        inner_radiation_types_frame.config(pady=10)

        # Logic for when a radiation type is selected
        def on_select():
            root.focus()
            with shelve.open(db_path) as shelve_prefs:
                shelve_prefs["rad_types"] = set(get_interactions(rad_types, rad_type_vars))

        # List of radiation types
        rad_types = [
            "Gamma Ray", "Prompt Gamma Ray",
            "Delayed Gamma Ray", "Annihilation Photon",
            "X-Ray", "Beta- Particle",
            "Delayed Beta Particle", "Beta+ Particle",
            "Internal Conversion Electron", "Auger Electron",
            "Alpha Particle", "Alpha Recoil Nucleus",
            "Fission Fragment", "Neutron",
        ]

        # List of neutron relevant radiation types
        neutron_relevant_types = [
            "Prompt Gamma Ray",
            "Delayed Gamma Ray",
            "Delayed Beta Particle",
            "Alpha Recoil Nucleus",
            "Fission Fragment",
            "Neutron",
        ]

        # Variables for each radiation type
        rad_type_vars = [tk.IntVar(value=1 if rad_type in selected_rad_types else 0) for rad_type in rad_types]

        # Frame for radiation type checkboxes
        checks = tk.Frame(inner_radiation_types_frame, bg="#F2F2F2")
        checks.pack()

        # Checkboxes for each radiation type
        for index, rad_type in enumerate(rad_types):
            if rad_type in neutron_relevant_types:
                continue
            interaction_checkbox(checks, rad_type_vars[index], rad_type, on_select)

        # Checkboxes for each neutron relevant radiation type
        nr_rad_type_checks = []

        # Creates toggle functionality
        show = False

        # Logic for when neutron relevant types are toggled
        def toggle():
            nonlocal show, index, rad_type
            root.focus()
            show = not show
            if show:
                button_text = "Hide Neutron Relevant Types"
                toggle_button.config(text=button_text, width=get_width([button_text]))

                for index, rad_type in enumerate(rad_types):
                    if rad_type in neutron_relevant_types:
                        nr_rad_type_checks.append(interaction_checkbox(checks, rad_type_vars[index],
                                                                       rad_type, on_select))
            else:
                button_text = "Show Neutron Relevant Types"
                toggle_button.config(text=button_text, width=get_width([button_text]))

                for check in nr_rad_type_checks:
                    check.destroy()
                nr_rad_type_checks.clear()

                # Makes sure we don't include neutron relevant types if they are hidden
                for index, rad_type in enumerate(rad_types):
                    if rad_type in neutron_relevant_types:
                        rad_type_vars[index].set(0)

        # Creates toggle button to show/hide neutron relevant radiation types
        toggle_button = ttk.Button(inner_radiation_types_frame, text="Show Neutron Relevant Types",
                                   style="Maize.TButton", padding=(0, 0),
                                   command=toggle)
        toggle_button.config(width=get_width(["Show Neutron Relevant Types"]))
        toggle_button.pack(pady=5)

        # Spacer
        empty_frame2 = make_spacer(root)

        # Frame for sorting exported data
        sort_frame = SectionFrame(root, title="Sort Data")
        sort_frame.pack()
        inner_sort_frame = sort_frame.get_inner_frame()

        # Sets back to default sort
        def default_sort():
            root.focus()
            var_column.set("Radiation Type")
            var_order.set("Ascending")
            with shelve.open(db_path) as shelve_prefs:
                shelve_prefs["column"] = "Radiation Type"
                shelve_prefs["order"] = "Ascending"

        # Creates button to set sort to default sort
        default_button = ttk.Button(inner_sort_frame, text="Default",
                                    style="Maize.TButton", padding=(0, 0),
                                    command=lambda: default_sort())
        default_button.config(width=get_width(["Default"]))
        default_button.pack(pady=(20,0))

        # Horizontal frame for column settings
        column_side_frame = tk.Frame(inner_sort_frame, bg="#F2F2F2")
        column_side_frame.pack(pady=(20,0))

        # Column label
        column_label = ttk.Label(column_side_frame, text="Column:", style="Black.TLabel")
        column_label.pack(side='left', padx=5)

        # Stores column and sets default
        var_column = tk.StringVar(root)
        var_column.set(sort_column)

        # Logic for when a column is selected
        def select_column(event):
            root.focus()
            event.widget.selection_clear()
            with shelve.open(db_path) as shelve_prefs:
                shelve_prefs["column"] = var_column.get()

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

        # Stores order and sets default
        var_order = tk.StringVar(root)
        var_order.set(sort_order)

        # Logic for when an order is selected
        def select_order(event):
            root.focus()
            event.widget.selection_clear()
            with shelve.open(db_path) as shelve_prefs:
                shelve_prefs["order"] = var_order.get()

        # Creates dropdown menu for orders
        order_choices = ["Ascending",
                         "Descending"]
        _ = make_unit_dropdown(order_side_frame, var_order, order_choices, select_order)

        # Spacer
        empty_frame3 = make_spacer(root)

        # Frame for setting filters
        filter_frame = SectionFrame(root, title="Set Filter")
        filter_frame.pack()
        inner_filter_frame = filter_frame.get_inner_frame()

        # Input box width
        entry_width = 5 if platform.system() == "Windows" else 6

        # Update filter type
        def select_filter_type(event):
            root.focus()
            event.widget.selection_clear()
            with shelve.open(db_path) as shelve_prefs:
                shelve_prefs["filter_type"] = var_filter.get()

        # Frame for filter type selection
        filter_type_frame = tk.Frame(inner_filter_frame, bg="#F2F2F2")
        filter_type_frame.pack(pady=(15,5))

        # Stores filter type and sets default
        var_filter = tk.StringVar(root)
        var_filter.set(filter_type)

        # Filter Type label
        basic_label(filter_type_frame, "Filter Type:")

        # Filter Type dropdown
        filter_choices = ["Yield", "Energy * Yield"]
        _ = make_dropdown(filter_type_frame, var_filter, filter_choices, select_filter_type)

        # Update filter type
        def select_filter_direction(event):
            root.focus()
            event.widget.selection_clear()
            with shelve.open(db_path) as shelve_prefs:
                shelve_prefs["filter_dir"] = var_filter_dir.get()

        # Frame for filter direction selection
        filter_dir_frame = tk.Frame(inner_filter_frame, bg="#F2F2F2")
        filter_dir_frame.pack(pady=(5,5))

        # Stores filter direction and sets default
        var_filter_dir = tk.StringVar(root)
        var_filter_dir.set(filter_dir)

        # Filter Direction label
        basic_label(filter_dir_frame, "Filter Direction:")

        # Filter Direction dropdown
        filter_dir_choices = ["Top", "Bottom"]
        _ = make_dropdown(filter_dir_frame, var_filter_dir, filter_dir_choices, select_filter_direction)

        # Frame for filter entry
        filter_entry_frame = tk.Frame(inner_filter_frame, bg="#F2F2F2")
        filter_entry_frame.pack(pady=(5,15))

        # Filter label
        basic_label(filter_entry_frame, "Filter:")

        # Horizontal frame for filter settings
        filter_side_frame = tk.Frame(filter_entry_frame, bg="#F2F2F2")
        filter_side_frame.pack(pady=(0,10))

        # Stores filter entry
        var_filter_percentage = tk.StringVar(root)
        var_filter_percentage.set(filter_percentage)

        # Logic to save filter percentage
        def on_change(*_):
            with shelve.open(db_path) as shelve_prefs:
                shelve_prefs["filter_percentage"] = var_filter_percentage.get()
        var_filter_percentage.trace_add("write", on_change)

        # Filter entry
        filter_entry = tk.Entry(filter_side_frame, width=entry_width, insertbackground="black",
                                background="white", foreground="black", borderwidth=3, bd=3,
                                highlightthickness=0, relief='solid', font=monospace_font,
                                textvariable=var_filter_percentage)
        filter_entry.pack(side='left')

        # Min label
        filter_label = ttk.Label(filter_side_frame, text="%", style="Black.TLabel")
        filter_label.pack(side='left')

        # Spacer
        empty_frame4 = make_spacer(root)

    # Frame for units
    unit_frame = tk.Frame()

    # Spacer
    empty_frame5 = tk.Frame()

    # Unit options are only created if
    # Calculation Mode is Half Life
    if mode == "Half Life" or mode == "Energies":
        # Frame for units
        unit_frame = SectionFrame(root, title="Select Units")
        unit_frame.pack()
        inner_unit_frame = unit_frame.get_inner_frame()

        # Horizontal frame for unit settings
        unit_side_frame = tk.Frame(inner_unit_frame, bg="#F2F2F2")
        unit_side_frame.pack(pady=20)

        if mode == "Half Life":
            text = "Half Life Unit:"
            shelf_name = "hl_unit"
            default = half_life_unit
            units = half_life_units
        else:
            text = "Energy Unit:"
            shelf_name = "energy_unit"
            default = energy_unit
            units = list(energy_units.keys())

        # Unit label
        unit_label = ttk.Label(unit_side_frame, text=text, style="Black.TLabel")
        unit_label.pack(side='left', padx=5)

        # Logic for when a unit is selected
        def on_select_unit(event):
            event.widget.selection_clear()
            root.focus()
            selection = event.widget.get()
            with shelve.open(db_path) as shelve_prefs:
                shelve_prefs[shelf_name] = selection

        # Stores unit and sets default
        var_unit = tk.StringVar(root)
        var_unit.set(default)

        # Creates dropdown menu for unit
        _ = make_unit_dropdown(unit_side_frame, var_unit, units, on_select_unit)

        # Spacer
        empty_frame5 = make_spacer(root)

    # Frame for Export Menu, References, & Help
    bottom_frame = tk.Frame(root, bg="#F2F2F2")
    bottom_frame.pack(pady=5)

    if mode == "Energies":
        # Creates Export Menu button
        export_button = ttk.Button(bottom_frame, text="Export Menu", style="Maize.TButton",
                                   padding=(0,0),
                                   command=lambda:
                                   to_export_menu(root, category, mode, common_el, element, isotope))
        export_button.config(width=get_width(["Export Menu"]))
        export_button.pack(side='left', padx=5)

    # Creates References button
    references_button = ttk.Button(bottom_frame, text="References", style="Maize.TButton",
                                   padding=(0,0),
                                   command=lambda: open_ref(root))
    references_button.config(width=get_width(["References"]))
    references_button.pack(side='left', padx=5)

    # Creates Help button
    help_button = ttk.Button(bottom_frame, text="Help", style="Maize.TButton",
                             padding=(0,0),
                             command=lambda: open_help(root))
    help_button.config(width=get_width(["Help"]))
    help_button.pack(side='left', padx=5)

    # Creates Back button to return to decay information main screen
    back_button = make_back_button(root, lambda: to_main(root, category, mode, common_el,
                                                         element, isotope))

    # Stores nodes into global list
    advanced_list = [title_frame,
                     a_r_frame, empty_frame1,
                     radiation_types_frame, empty_frame2,
                     sort_frame, empty_frame3,
                     filter_frame, empty_frame4,
                     unit_frame, empty_frame5,
                     bottom_frame, back_button]

#####################################################################################
# NAVIGATION SECTION
#####################################################################################

"""
This function clears the decay information advanced screen
in preparation for opening a different screen.
"""
def clear_advanced():
    global advanced_list

    # Clears decay information advanced screen
    for node in advanced_list:
        node.destroy()
    advanced_list.clear()

"""
This function transitions from the decay information advanced screen
to the decay information main screen by first clearing the
decay information advanced screen and then creating the
decay information main screen.
It is called when the Back button is hit.
"""
def to_main(root, category, mode, common_el, element, isotope):
    from App.Decay.Information.decay_info_main import decay_info_main

    clear_advanced()
    decay_info_main(root, category, mode, common_el, element, isotope)
    scroll_to_top()

"""
This function transitions from the decay information advanced screen
to the decay information export screen by first clearing the
decay information advanced screen and then creating the
decay information export screen.
It is called when the Export Menu button is hit.
"""
def to_export_menu(root, category, mode, common_el, element, isotope):
    clear_advanced()
    decay_info_export(root, category, mode, common_el, element, isotope)
    scroll_to_top()

"""
This function opens the decay information References.txt file.
"""
def open_ref(root):
    root.focus()
    db_path = resource_path('Utility/Modules/Decay/Information/References.txt')
    open_file(db_path)

"""
This function opens the decay information Help.txt file.
"""
def open_help(root):
    root.focus()
    db_path = resource_path('Utility/Modules/Decay/Information/Help.txt')
    open_file(db_path)