##### IMPORTS #####
import platform
import tkinter as tk
from tkinter import ttk
import tkinter.font as font
from App.style import SectionFrame
from Core.Decay.Information.energies_export import export_data
from Utility.Functions.logic_utility import get_item, get_interactions
from Utility.Functions.gui_utility import (
    basic_label,
    make_title_frame,
    make_back_button,
    make_spacer, get_width,
    make_dropdown, make_unit_dropdown, interaction_checkbox
)

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

    neutron_relevant_types = [
        "Prompt Gamma Ray",
        "Delayed Gamma Ray",
        "Delayed Beta Particle",
        "Alpha Recoil Nucleus",
        "Fission Fragment",
        "Neutron",
    ]

    # Variables for each radiation type
    rad_type_vars = [tk.IntVar(value=1 if not rad_type in neutron_relevant_types else 0) for rad_type in rad_types]

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
    def toggle():
        nonlocal show, index, rad_type
        root.focus()
        show = not show
        if show:
            text = "Hide Neutron Relevant Types"
            toggle_button.config(text=text, width=get_width([text]))

            for index, rad_type in enumerate(rad_types):
                if rad_type in neutron_relevant_types:
                    nr_rad_type_checks.append(interaction_checkbox(checks, rad_type_vars[index],
                                                                   rad_type, on_select))
        else:
            text = "Show Neutron Relevant Types"
            toggle_button.config(text=text, width=get_width([text]))

            for check in nr_rad_type_checks:
                check.destroy()
            nr_rad_type_checks.clear()

            # Makes sure we don't include neutron relevant types if they are hidden
            for index, rad_type in enumerate(rad_types):
                if rad_type in neutron_relevant_types:
                    rad_type_vars[index].set(0)

    # Creates toggle button to show/hide neutron relevant radiation types
    toggle_button = ttk.Button(inner_radiation_types_frame, text="Show Neutron Relevant Types",
                               style="Maize.TButton", padding=(0,0),
                               command=toggle)
    toggle_button.config(width=get_width(["Show Neutron Relevant Types"]))
    toggle_button.pack(pady=5)

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

    # Frame for setting filters
    filter_frame = SectionFrame(root, title="Set Filter")
    filter_frame.pack()
    inner_filter_frame = filter_frame.get_inner_frame()

    # Input box width
    entry_width = 5 if platform.system() == "Windows" else 6

    # Clear selection
    def on_dropdown_change(event):
        root.focus()
        event.widget.selection_clear()

    # Frame for filter type selection
    filter_type_frame = tk.Frame(inner_filter_frame, bg="#F2F2F2")
    filter_type_frame.pack(pady=(15,5))

    # Stores filter type and sets default
    var_filter = tk.StringVar(root)
    var_filter.set("Yield")

    # Filter Type label
    basic_label(filter_type_frame, "Filter Type:")

    # Filter Type dropdown
    filter_choices = ["Yield", "Energy * Yield"]
    _ = make_dropdown(filter_type_frame, var_filter, filter_choices, on_dropdown_change)

    # Frame for filter direction selection
    filter_dir_frame = tk.Frame(inner_filter_frame, bg="#F2F2F2")
    filter_dir_frame.pack(pady=(5,5))

    # Stores filter direction and sets default
    var_filter_dir = tk.StringVar(root)
    var_filter_dir.set("Top")

    # Filter Direction label
    basic_label(filter_dir_frame, "Filter Direction:")

    # Filter Direction dropdown
    filter_dir_choices = ["Top", "Bottom"]
    _ = make_dropdown(filter_dir_frame, var_filter_dir, filter_dir_choices, on_dropdown_change)

    # Frame for filter entry
    filter_entry_frame = tk.Frame(inner_filter_frame, bg="#F2F2F2")
    filter_entry_frame.pack(pady=(5,15))

    # Filter label
    basic_label(filter_entry_frame, "Filter:")

    # Horizontal frame for filter settings
    filter_side_frame = tk.Frame(filter_entry_frame, bg="#F2F2F2")
    filter_side_frame.pack(pady=(0,10))

    # Filter entry
    filter_entry = tk.Entry(filter_side_frame, width=entry_width, insertbackground="black",
                            background="white", foreground="black", borderwidth=3, bd=3,
                            highlightthickness=0, relief='solid', font=monospace_font)
    filter_entry.insert(0, "100")
    filter_entry.pack(side='left')

    # Min label
    filter_label = ttk.Label(filter_side_frame, text="%", style="Black.TLabel")
    filter_label.pack(side='left')

    # Spacer
    empty_frame3 = make_spacer(root)

    # Frame for options
    options_frame = SectionFrame(root, title="Export Options")
    options_frame.pack()
    inner_options_frame = options_frame.get_inner_frame()

    # Creates Export button
    export_button = ttk.Button(inner_options_frame, text="Export", style="Maize.TButton",
                               padding=(0,0),
                               command=lambda:
                               export_data(root,
                                           get_item(category, common_el, "", element, "", ""),
                                           set(get_interactions(rad_types, rad_type_vars)),
                                           isotope, error_label, var_column.get(),
                                           var_order.get(), var_filter.get(),
                                           var_filter_dir.get(), filter_entry.get()
                                           ))
    export_button.config(width=get_width(["Export"]))
    export_button.pack(pady=(20,5))

    # Creates error label for bad input
    error_label = ttk.Label(inner_options_frame, text="", style="Error.TLabel")
    error_label.pack(pady=(5,10))

    # Creates Back button to return to decay information advanced screen
    back_button = make_back_button(root, lambda: advanced_back(root, category, mode,
                                                               common_el, element, isotope))

    # Stores nodes into global list
    export_list = [title_frame,
                   radiation_types_frame, empty_frame1,
                   sort_frame, empty_frame2,
                   filter_frame, empty_frame3,
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