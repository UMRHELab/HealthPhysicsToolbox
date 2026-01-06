##### IMPORTS #####
import shelve
import tkinter as tk
from tkinter import ttk
from App.style import SectionFrame
from Utility.Functions.choices import get_choices, get_successors
from Utility.Functions.files import resource_path, open_file, get_user_data_path
from Utility.Functions.gui_utility import (
    basic_label,
    make_back_button,
    interaction_checkbox,
    make_spacer, get_width,
    make_title_frame, make_vertical_frame,
    make_unit_dropdown, make_action_dropdown
)

# For global access to nodes on decay calculator advanced screen
advanced_list = []

#####################################################################################
# MENU SECTION
#####################################################################################

"""
This function sets up the decay calculator advanced screen.
The following sections and widgets are created:
   Module Title (Decay Calculator)
   Customize Common Elements section
   Select Units section
   Desired Nuclides for Isotope section
   References button
   Help button
   Back button
This function contains all of the logic involving these widgets'
behaviors.
The sections and widgets are stored in advanced_list so they can be
accessed later by clear_advanced.
"""
def decay_calc_advanced(root, category, mode, common_el, element, isotope,
                        dates, nuclide_vars):
    global advanced_list

    # Gets units from user prefs
    db_path = get_user_data_path("Settings/Decay/Calculator")
    with shelve.open(db_path) as prefs:
        amount_type = prefs.get("amount_type", "Activity (Bq)")
        amount_unit = prefs.get("amount_unit", "Bq")
        time_unit = prefs.get("time_unit", "s")

    # Makes title frame
    title_frame = make_title_frame(root, "Decay Calculator", "Decay/Calculator")

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

    # Frame for units
    unit_frame = SectionFrame(root, title="Select Units")
    unit_frame.pack()
    inner_unit_frame = unit_frame.get_inner_frame()

    # Stores whether dates are used
    var_dates = tk.IntVar()
    var_dates.set(dates)

    def on_use_dates():
        nonlocal dates
        dates = var_dates.get()
        if dates:
            time_unit_dropdown.config(state='disabled')
        else:
            time_unit_dropdown.config(state='enabled')
        root.focus()

    # Creates checkbox for using dates
    use_dates = ttk.Checkbutton(inner_unit_frame, text="Use Dates Instead of Time Elapsed",
                                variable=var_dates, style="Maize.TCheckbutton",
                                command=on_use_dates)
    use_dates.pack(pady=(25,0))

    # Horizontal frame for time unit settings
    time_unit_side_frame = tk.Frame(inner_unit_frame, bg="#F2F2F2")
    time_unit_side_frame.pack(pady=20)

    # Time unit label
    time_unit_label = ttk.Label(time_unit_side_frame, text="Time Units:", style="Black.TLabel")
    time_unit_label.pack(side='left', padx=5)

    # Logic for when time unit is selected
    def on_select_time_unit(event):
        event.widget.selection_clear()
        root.focus()
        selection = event.widget.get()
        with shelve.open(db_path) as shelve_prefs:
            shelve_prefs["time_unit"] = selection

    # Stores time unit and sets default
    var_time = tk.StringVar(root)
    var_time.set(time_unit)

    # Creates dropdown menu for time unit
    time_choices = ['μs', 'ms', 's', 'm', 'h', 'd', 'y']
    time_unit_dropdown = make_unit_dropdown(time_unit_side_frame, var_time, time_choices,
                                            on_select_time_unit)

    # Horizontal frame for amount unit settings
    amount_unit_side_frame = tk.Frame(inner_unit_frame, bg="#F2F2F2")
    amount_unit_side_frame.pack(pady=(0,20))

    # Amount unit label
    amount_unit_label = ttk.Label(amount_unit_side_frame, text="Amount Units:", style="Black.TLabel")
    amount_unit_label.pack(side='left', padx=5)

    # Logic for when an amount type is selected
    def on_select_amount_type(event):
        event.widget.selection_clear()
        selection = event.widget.get()

        with shelve.open(db_path) as shelve_prefs:
            og_amount_type = shelve_prefs.get("amount_type", "Activity (Bq)")

        # Adjusts unit choices
        unit_choices = amount_choices[selection]
        if og_amount_type != selection:
            with shelve.open(db_path) as shelve_prefs:
                shelve_prefs["amount_unit"] = default_choices[selection]
                amount_unit_dropdown.set(default_choices[selection])
                amount_unit_dropdown.config(values=unit_choices,
                                            width=get_width(unit_choices))

        with shelve.open(db_path) as shelve_prefs:
            shelve_prefs["amount_type"] = selection
        root.focus()

    # Possible amount unit types
    amount_types = ["Activity (Bq)",
                    "Activity (Ci)",
                    "Activity (dpm)",
                    "Mass",
                    "Moles",
                    "Nuclei Number"]

    # Stores amount type and sets default
    var_amount_type = tk.StringVar(root)
    var_amount_type.set(amount_type)

    # Creates dropdown menu for amount type
    _ = make_unit_dropdown(amount_unit_side_frame, var_amount_type, amount_types, on_select_amount_type)

    # Logic for when amount unit is selected
    def on_select_amount_unit(event):
        event.widget.selection_clear()
        root.focus()
        selection = event.widget.get()
        with shelve.open(db_path) as shelve_prefs:
            shelve_prefs["amount_unit"] = selection

    # Possible amount unit choices
    default_choices = {
        "Activity (Bq)": "Bq",
        "Activity (Ci)": "Ci",
        "Activity (dpm)": "dpm",
        "Mass": "g",
        "Moles": "mol",
        "Nuclei Number": "num"
    }
    amount_choices = {
        "Activity (Bq)": ["pBq", "nBq", "μBq", "mBq", "Bq", "kBq", "MBq", "GBq", "TBq"],
        "Activity (Ci)": ["pCi", "nCi", "μCi", "mCi", "Ci", "kCi", "MCi", "GCi", "TCi"],
        "Activity (dpm)": ["dpm"],
        "Mass": ["pg", "ng", "μg", "mg", "g", "kg", "t"],
        "Moles": ["pmol", "nmol", "μmol", "mmol", "mol", "kmol", "Mmol"],
        "Nuclei Number": ["num"]
    }

    # Stores amount unit and sets default
    var_amount = tk.StringVar(root)
    var_amount.set(amount_unit)

    # Creates dropdown menu for amount unit
    amount_unit_dropdown = make_unit_dropdown(amount_unit_side_frame, var_amount,
                                              amount_choices[amount_type],
                                              on_select_amount_unit)

    # Spacer
    empty_frame2 = make_spacer(root)

    # Gets successors of isotope
    successors = get_successors(isotope)

    # Frame for nuclide selection settings
    nuclides_frame = SectionFrame(root, title="Desired Nuclides for " + isotope)

    # Spacer
    empty_frame3 = tk.Frame()

    # Frame for checkboxes
    if len(successors) != 0:
        nuclides_frame.pack()
        inner_nuclides_frame = nuclides_frame.get_inner_frame()
        inner_nuclides_frame.config(pady=10)

        checks = tk.Frame(inner_nuclides_frame, bg="#F2F2F2")
        checks.pack()

        for successor in successors:
            interaction_checkbox(checks, nuclide_vars[successor], successor,
                                 lambda: root.focus())

        # Spacer
        empty_frame3 = make_spacer(root)

    # Frame for References, & Help
    bottom_frame = tk.Frame(root, bg="#F2F2F2")
    bottom_frame.pack(pady=5)

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

    # Creates Back button to return to decay calculator main screen
    back_button = make_back_button(root, lambda: to_main(root, category, mode, common_el,
                                                         element, isotope, dates, nuclide_vars))

    # Stores nodes into global list
    advanced_list = [title_frame,
                     a_r_frame, empty_frame1,
                     unit_frame, empty_frame2,
                     nuclides_frame, empty_frame3,
                     bottom_frame, back_button]

#####################################################################################
# NAVIGATION SECTION
#####################################################################################

"""
This function clears the decay calculator advanced screen
in preparation for opening a different screen.
"""
def clear_advanced():
    global advanced_list

    # Clears decay calculator advanced screen
    for node in advanced_list:
        node.destroy()
    advanced_list.clear()

"""
This function transitions from the decay calculator advanced screen
to the decay calculator main screen by first clearing the
decay calculator advanced screen and then creating the
decay calculator main screen.
It is called when the Back button is hit.
"""
def to_main(root, category, mode, common_el, element, isotope, dates, nuclide_vars):
    from App.Decay.Calculator.decay_calc_main import decay_calc_main

    clear_advanced()
    decay_calc_main(root, category, mode, common_el, element, isotope, dates, nuclide_vars)

"""
This function opens the decay calculator References.txt file.
"""
def open_ref(root):
    root.focus()
    db_path = resource_path('Utility/Modules/Decay/Calculator/References.txt')
    open_file(db_path)

"""
This function opens the decay calculator Help.txt file.
"""
def open_help(root):
    root.focus()
    db_path = resource_path('Utility/Modules/Decay/Calculator/Help.txt')
    open_file(db_path)