##### IMPORTS #####
import tkinter as tk
from App.scroll import scroll_to_top
from App.Dose.ICRP68.icrp68_export import icrp68_export
from Utility.Functions.files import resource_path, open_file
from Utility.Functions.gui_utility import (
    make_spacer,
    make_back_button,
    make_title_frame,
    make_customize_common_elements_frame,
    make_export_menu_button, make_references_button, make_help_button
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
def icrp68_advanced(root, category, mode, coefficient, common_el, element, isotope):
    global advanced_list

    # Makes title frame
    title_frame = make_title_frame(root, "ICRP68 Coefficients", "Dose/ICRP68")

    # Frame for add/remove settings
    a_r_frame = make_customize_common_elements_frame(root, "Dose", "ICRP68")

    # Spacer
    empty_frame1 = make_spacer(root)

    # Frame for Export Menu, References, & Help
    bottom_frame = tk.Frame(root, bg="#F2F2F2")
    bottom_frame.pack(pady=5)

    # Creates Export Menu button
    make_export_menu_button(bottom_frame, lambda: to_export_menu(root, category, mode, coefficient,
                                                                 common_el, element, isotope))

    # Creates References & Help buttons
    make_references_button(bottom_frame, lambda: open_ref(root))
    make_help_button(bottom_frame, lambda: open_help(root))

    # Creates Back button to return to ICRP68 main screen
    back_button = make_back_button(root, lambda: to_main(root, category, mode, coefficient,
                                                         common_el, element, isotope))

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
def to_main(root, category, mode, coefficient, common_el, element, isotope):
    from App.Dose.ICRP68.icrp68_main import icrp68_main

    clear_advanced()
    icrp68_main(root, category, mode, coefficient, common_el, element, isotope)
    scroll_to_top()

"""
This function transitions from the ICRP68 advanced screen
to the ICRP68 export screen by first clearing the
ICRP68 advanced screen and then creating the
ICRP68 export screen.
It is called when the Export Menu button is hit.
"""
def to_export_menu(root, category, mode, coefficient, common_el, element, isotope):
    clear_advanced()
    icrp68_export(root, category, mode, coefficient, common_el, element, isotope)
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