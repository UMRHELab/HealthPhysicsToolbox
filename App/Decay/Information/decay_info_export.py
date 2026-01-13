##### IMPORTS #####
from tkinter import ttk
from App.style import SectionFrame
from App.scroll import scroll_to_top
from Utility.Functions.logic_utility import get_item
from Core.Decay.Information.energies_export import export_data
from Utility.Functions.gui_utility import (
    make_title_frame,
    make_back_button, make_export_button
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

    # Frame for options
    options_frame = SectionFrame(root, title="Export Options")
    options_frame.pack()
    inner_options_frame = options_frame.get_inner_frame()

    # Creates Export button
    make_export_button(inner_options_frame, lambda:
                                    export_data(root, get_item(category, common_el, "", element, "", ""),
                                                isotope, error_label),
                       pady=(20,5))

    # Creates error label for bad input
    error_label = ttk.Label(inner_options_frame, text="", style="Error.TLabel")
    error_label.pack(pady=(5,10))

    # Creates Back button to return to decay information advanced screen
    back_button = make_back_button(root, lambda: advanced_back(root, category, mode,
                                                               common_el, element, isotope))

    # Stores nodes into global list
    export_list = [title_frame,
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
    scroll_to_top()