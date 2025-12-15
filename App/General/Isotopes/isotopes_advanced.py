##### IMPORTS #####
import shelve
import tkinter as tk
from tkinter import ttk
from App.style import SectionFrame
from Utility.Functions.choices import get_choices
from Utility.Functions.gui_utility import make_vertical_frame
from Utility.Functions.gui_utility import make_spacer, get_width
from Utility.Functions.gui_utility import make_title_frame, basic_label
from Utility.Functions.files import resource_path, open_file, get_user_data_path
from Utility.Functions.gui_utility import make_unit_dropdown, make_action_dropdown
from Utility.Functions.math_utility import atomic_mass_numerator, atomic_mass_denominator

# For global access to nodes on isotopes advanced screen
advanced_list = []

#####################################################################################
# MENU SECTION
#####################################################################################

"""
This function sets up the general isotopes advanced screen.
The following sections and widgets are created:
   Module Title (Isotope Information)
   Customize Common Elements section
   Select Units section
   References button
   Help button
   Back button
This function contains all of the logic involving these widgets'
behaviors.
The sections and widgets are stored in advanced_list so they can be
accessed later by clear_advanced.
"""
def isotopes_advanced(root, category, mode, common_el, element):
    global advanced_list

    # Gets atomic mass units from user prefs
    db_path = get_user_data_path("Settings/General/Isotopes")
    with shelve.open(db_path) as prefs:
        am_num = prefs.get("am_num", "g")
        am_den = prefs.get("am_den", "mol")

    # Makes title frame
    title_frame = make_title_frame(root, "Isotope Information", "General/Isotopes")

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
    unit_frame = tk.Frame()

    # Spacer
    empty_frame2 = tk.Frame()

    # Unit options are only created if
    # Calculation Mode is Atomic Mass
    if mode == "Atomic Mass":
        # Frame for units
        unit_frame = SectionFrame(root, title="Select Units")
        unit_frame.pack()
        inner_unit_frame = unit_frame.get_inner_frame()

        # Horizontal frame for unit settings
        unit_side_frame = tk.Frame(inner_unit_frame, bg="#F2F2F2")
        unit_side_frame.pack(pady=20)

        # Unit label
        unit_label = ttk.Label(unit_side_frame, text=mode + " Units:", style="Black.TLabel")
        unit_label.pack(side='left', padx=5)

        # Logic for when a numerator is selected
        def on_select_num(event):
            event.widget.selection_clear()
            root.focus()
            selection = event.widget.get()
            with shelve.open(db_path) as shelve_prefs:
                shelve_prefs["am_num"] = selection

        # Logic for when a denominator is selected
        def on_select_den(event):
            event.widget.selection_clear()
            root.focus()
            selection = event.widget.get()
            with shelve.open(db_path) as shelve_prefs:
                shelve_prefs["am_den"] = selection

        # Stores numerator and sets default
        var_numerator = tk.StringVar(root)
        var_numerator.set(am_num)

        # Creates dropdown menu for numerator unit
        _ = make_unit_dropdown(unit_side_frame, var_numerator, list(atomic_mass_numerator.keys()), on_select_num)

        # / label
        slash_label = ttk.Label(unit_side_frame, text="/", style="Black.TLabel")
        slash_label.pack(side='left')

        # Stores denominator and sets default
        var_denominator = tk.StringVar(root)
        var_denominator.set(am_den)

        # Creates dropdown menu for denominator unit
        _ = make_unit_dropdown(unit_side_frame, var_denominator, list(atomic_mass_denominator.keys()), on_select_den)

        # Spacer
        empty_frame2 = make_spacer(root)

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

    # Creates Back button to return to isotopes main screen
    back_button = ttk.Button(root, text="Back", style="Maize.TButton",
                             padding=(0,0),
                             command=lambda: to_main(root, category, mode, common_el, element))
    back_button.config(width=get_width(["Back"]))
    back_button.pack(pady=5)

    # Stores nodes into global list
    advanced_list = [title_frame,
                     a_r_frame, empty_frame1,
                     unit_frame, empty_frame2,
                     bottom_frame, back_button]

#####################################################################################
# NAVIGATION SECTION
#####################################################################################

"""
This function clears the isotopes advanced screen
in preparation for opening a different screen.
"""
def clear_advanced():
    global advanced_list

    # Clears isotopes advanced screen
    for node in advanced_list:
        node.destroy()
    advanced_list.clear()

"""
This function transitions from the isotopes advanced screen
to the isotopes main screen by first clearing the
isotopes advanced screen and then creating the
isotopes main screen.
It is called when the Back button is hit.
"""
def to_main(root, category, mode, common_el, element):
    from App.General.Isotopes.isotopes_main import isotopes_main

    clear_advanced()
    isotopes_main(root, category, mode, common_el, element)

"""
This function opens the isotopes References.txt file.
"""
def open_ref(root):
    root.focus()
    db_path = resource_path('Utility/Modules/General/Isotopes/References.txt')
    open_file(db_path)

"""
This function opens the isotopes Help.txt file.
"""
def open_help(root):
    root.focus()
    db_path = resource_path('Utility/Modules/General/Isotopes/Help.txt')
    open_file(db_path)