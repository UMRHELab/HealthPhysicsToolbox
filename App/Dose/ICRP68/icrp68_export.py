##### IMPORTS #####
from tkinter import ttk
from App.style import SectionFrame
from App.scroll import scroll_to_top
from Core.Dose.ICRP68.icrp68_data import export_data
from Utility.Functions.logic_utility import get_item
from Utility.Functions.gui_utility import (
    get_width,
    make_title_frame,
    make_back_button,
)

# For global access to nodes on ICRP68 export screen
export_list = []

#####################################################################################
# MENU SECTION
#####################################################################################

"""
This function sets up the ICRP68 export screen.
The following sections and widgets are created:
   Module Title (ICRP68 Coefficients)
   Export Options section
   Back button
This function contains all of the logic involving these widgets'
behaviors.
The sections and widgets are stored in export_list so they can be
accessed later by clear_export.
"""
def icrp68_export(root, category, mode, common_el, element, isotope):
    global export_list

    # Makes title frame
    title_frame = make_title_frame(root, "ICRP68 Coefficients", "Dose/ICRP68")

    # Frame for options
    options_frame = SectionFrame(root, title="Export Options")
    options_frame.pack()
    inner_options_frame = options_frame.get_inner_frame()

    # Creates Export button
    export_button = ttk.Button(inner_options_frame, text="Export", style="Maize.TButton",
                               padding=(0,0),
                               command=lambda:
                               export_data(root, mode, get_item(category, common_el, "", element, "", ""),
                                           isotope, error_label))
    export_button.config(width=get_width(["Export"]))
    export_button.pack(pady=(20,5))

    # Creates error label for bad input
    error_label = ttk.Label(inner_options_frame, text="", style="Error.TLabel")
    error_label.pack(pady=(5,10))

    # Creates Back button to return to ICRP68 advanced screen
    back_button = make_back_button(root, lambda: advanced_back(root, category, mode,
                                                               common_el, element, isotope))

    # Stores nodes into global list
    export_list = [title_frame,
                   options_frame, back_button]

#####################################################################################
# NAVIGATION SECTION
#####################################################################################

"""
This function clears the ICRP68 export screen
in preparation for opening a different screen.
"""
def clear_export():
    global export_list

    # Clears ICRP68 export screen
    for node in export_list:
        node.destroy()
    export_list.clear()

"""
This function transitions from the ICRP68 export screen
to the ICRP68 advanced screen by first clearing the
ICRP68 export screen and then creating the
ICRP68 advanced screen.
It is called when the Back button is hit.
"""
def advanced_back(root, category, mode, common_el, element, isotope):
    from App.Dose.ICRP68.icrp68_advanced import icrp68_advanced

    clear_export()
    icrp68_advanced(root, category, mode, common_el, element, isotope)
    scroll_to_top()