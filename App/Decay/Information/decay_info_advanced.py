##### IMPORTS #####
import shelve
import tkinter as tk
from tkinter import ttk
from App.style import SectionFrame
from Utility.Functions.choices import get_choices
from Utility.Functions.files import get_user_data_path
from Utility.Functions.files import resource_path, open_file
from Utility.Functions.gui_utility import make_vertical_frame
from Core.Decay.Information.nuclide_info import half_life_units
from Utility.Functions.gui_utility import make_spacer, get_width
from App.Decay.Information.decay_info_export import decay_info_export
from Utility.Functions.gui_utility import make_title_frame, basic_label
from Utility.Functions.gui_utility import make_unit_dropdown, make_action_dropdown

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

    # Gets half-life unit from user prefs
    db_path = get_user_data_path("Settings/Decay/Information")
    with shelve.open(db_path) as prefs:
        half_life_unit = prefs.get("hl_unit", "s")

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

    # Frame for units
    unit_frame = tk.Frame()

    # Spacer
    empty_frame2 = tk.Frame()

    # Unit options are only created if
    # Calculation Mode is Half Life
    if mode == "Half Life":
        # Frame for units
        unit_frame = SectionFrame(root, title="Select Units")
        unit_frame.pack()
        inner_unit_frame = unit_frame.get_inner_frame()

        # Horizontal frame for unit settings
        unit_side_frame = tk.Frame(inner_unit_frame, bg="#F2F2F2")
        unit_side_frame.pack(pady=20)

        # Unit label
        unit_label = ttk.Label(unit_side_frame, text=mode + " Unit:",
                               style="Black.TLabel")
        unit_label.pack(side='left', padx=5)

        # Logic for when a half-life unit is selected
        def on_select_unit(event):
            event.widget.selection_clear()
            root.focus()
            selection = event.widget.get()
            with shelve.open(db_path) as shelve_prefs:
                shelve_prefs["hl_unit"] = selection

        # Stores half life unit and sets default
        var_unit = tk.StringVar(root)
        var_unit.set(half_life_unit)

        # Creates dropdown menu for unit
        _ = make_unit_dropdown(unit_side_frame, var_unit, half_life_units, on_select_unit)

        # Spacer
        empty_frame2 = make_spacer(root)

    # Frame for Export Menu, References, & Help
    bottom_frame = tk.Frame(root, bg="#F2F2F2")
    bottom_frame.pack(pady=5)

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
    back_button = ttk.Button(root, text="Back", style="Maize.TButton",
                             padding=(0,0),
                             command=lambda: to_main(root, category, mode, common_el,
                                                     element, isotope))
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