##### IMPORTS #####
import shelve
import tkinter as tk
from tkinter import ttk
from App.style import SectionFrame
from App.scroll import scroll_to_top
from Utility.Functions.choices import get_choices
from Utility.Functions.files import resource_path, open_file, get_user_data_path
from Utility.Functions.math_utility import atomic_mass_numerator, atomic_mass_denominator
from Utility.Functions.gui_utility import (
    basic_label,
    make_back_button,
    make_spacer, get_width,
    make_title_frame, make_vertical_frame,
    make_unit_dropdown, make_action_dropdown
)

# For global access to nodes on elements advanced screen
advanced_list = []

#####################################################################################
# MENU SECTION
#####################################################################################

"""
This function sets up the general elements advanced screen.
The following sections and widgets are created:
   Module Title (Element Information)
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
def elements_advanced(root, category, common_el, element):
    global advanced_list

    # Gets atomic mass units from user prefs
    db_path = get_user_data_path("Settings/General/Elements")
    with shelve.open(db_path) as prefs:
        am_num = prefs.get("am_num", "g")
        am_den = prefs.get("am_den", "mol")

    # Makes title frame
    title_frame = make_title_frame(root, "Element Information", "General/Elements")

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

    # Horizontal frame for unit settings
    unit_side_frame = tk.Frame(inner_unit_frame, bg="#F2F2F2")
    unit_side_frame.pack(pady=20)

    # Unit label
    unit_label = ttk.Label(unit_side_frame, text="Atomic Mass Units:", style="Black.TLabel")
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

    # Creates Back button to return to elements main screen
    back_button = make_back_button(root, lambda: to_main(root, category, common_el, element))

    # Stores nodes into global list
    advanced_list = [title_frame,
                     a_r_frame, empty_frame1,
                     unit_frame, empty_frame2,
                     bottom_frame, back_button]

#####################################################################################
# NAVIGATION SECTION
#####################################################################################

"""
This function clears the elements advanced screen
in preparation for opening a different screen.
"""
def clear_advanced():
    global advanced_list

    # Clears elements advanced screen
    for node in advanced_list:
        node.destroy()
    advanced_list.clear()

"""
This function transitions from the elements advanced screen
to the elements main screen by first clearing the
elements advanced screen and then creating the
elements main screen.
It is called when the Back button is hit.
"""
def to_main(root, category, common_el, element):
    from App.General.Elements.elements_main import elements_main

    clear_advanced()
    elements_main(root, category, common_el, element)
    scroll_to_top()

"""
This function opens the elements References.txt file.
"""
def open_ref(root):
    root.focus()
    db_path = resource_path('Utility/Modules/General/Elements/References.txt')
    open_file(db_path)

"""
This function opens the elements Help.txt file.
"""
def open_help(root):
    root.focus()
    db_path = resource_path('Utility/Modules/General/Elements/Help.txt')
    open_file(db_path)