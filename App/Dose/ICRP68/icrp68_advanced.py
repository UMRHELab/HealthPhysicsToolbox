##### IMPORTS #####
import tkinter as tk
from tkinter import ttk
from App.style import SectionFrame
from App.scroll import scroll_to_top
from Utility.Functions.choices import get_choices
from App.Dose.ICRP68.icrp68_export import icrp68_export
from Utility.Functions.files import resource_path, open_file
from Utility.Functions.gui_utility import (
    basic_label,
    make_back_button,
    make_action_dropdown,
    make_spacer, get_width,
    make_title_frame, make_vertical_frame,
)

# For global access to nodes on ICRP68 advanced screen
advanced_list = []

#####################################################################################
# MENU SECTION
#####################################################################################

"""
This function sets up the ICRP68 advanced screen.
The following sections and widgets are created:
   Module Title (ICRP68 Coefficients)
   Customize Common Elements section
   Export Menu button
   References button
   Help button
   Back button
This function contains all of the logic involving these widgets'
behaviors.
The sections and widgets are stored in advanced_list so they can be
accessed later by clear_advanced.
"""
def icrp68_advanced(root, category, mode, common_el, element, isotope):
    global advanced_list

    # Makes title frame
    title_frame = make_title_frame(root, "ICRP68 Coefficients", "Dose/ICRP68")

    # Gets common and non-common elements
    elements = get_choices("All Elements", "Dose", "ICRP68")
    common = get_choices("Common Elements", "Dose", "ICRP68")
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

    # Creates Back button to return to ICRP68 main screen
    back_button = make_back_button(root, lambda: to_main(root, category, mode, common_el, element, isotope))

    # Stores nodes into global list
    advanced_list = [title_frame,
                     a_r_frame, empty_frame1,
                     bottom_frame, back_button]

#####################################################################################
# NAVIGATION SECTION
#####################################################################################

"""
This function clears the ICRP68 advanced screen
in preparation for opening a different screen.
"""
def clear_advanced():
    global advanced_list

    # Clears ICRP68 advanced screen
    for node in advanced_list:
        node.destroy()
    advanced_list.clear()

"""
This function transitions from the ICRP68 advanced screen
to the ICRP68 main screen by first clearing the
ICRP68 advanced screen and then creating the
ICRP68 main screen.
It is called when the Back button is hit.
"""
def to_main(root, category, mode, common_el, element, isotope):
    from App.Dose.ICRP68.icrp68_main import icrp68_main

    clear_advanced()
    icrp68_main(root, category, mode, common_el, element, isotope)
    scroll_to_top()

"""
This function transitions from the ICRP68 advanced screen
to the ICRP68 export screen by first clearing the
ICRP68 advanced screen and then creating the
ICRP68 export screen.
It is called when the Export Menu button is hit.
"""
def to_export_menu(root, category, mode, common_el, element, isotope):
    clear_advanced()
    icrp68_export(root, category, mode, common_el, element, isotope)
    scroll_to_top()

"""
This function opens the ICRP68 References.txt file.
"""
def open_ref(root):
    root.focus()
    db_path = resource_path('Utility/Modules/Dose/ICRP68/References.txt')
    open_file(db_path)

"""
This function opens the ICRP68 Help.txt file.
"""
def open_help(root):
    root.focus()
    db_path = resource_path('Utility/Modules/Dose/ICRP68/Help.txt')
    open_file(db_path)