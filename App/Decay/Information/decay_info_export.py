##### IMPORTS #####
import tkinter as tk
from tkinter import ttk
from App.style import SectionFrame
from Core.Decay.Information.energies_export import export_data
from Utility.Functions.gui_utility import get_width, make_title_frame

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

    # Stores whether file is saved and sets default
    var_save = tk.IntVar()
    var_save.set(1)

    # Frame for options
    options_frame = SectionFrame(root, title="Export Options")
    options_frame.pack()
    inner_options_frame = options_frame.get_inner_frame()

    # Frame for export type
    export_frame = tk.Frame(inner_options_frame, bg="#F2F2F2")
    export_frame.pack(pady=5)

    # Creates Export button
    export_button = ttk.Button(inner_options_frame, text="Export", style="Maize.TButton",
                               padding=(0,0),
                               command=lambda:
                               export_data(root,
                                           element if category == "All Elements" else common_el,
                                           isotope, error_label))
    export_button.config(width=get_width(["Export"]))
    export_button.pack(pady=(10,5))

    # Creates error label for bad input
    error_label = ttk.Label(inner_options_frame, text="", style="Error.TLabel")
    error_label.pack(pady=(5,10))

    # Creates Back button to return to decay information advanced screen
    back_button = ttk.Button(root, text="Back", style="Maize.TButton", padding=(0,0),
                             command=lambda: advanced_back(root, category, mode,
                                                           common_el, element, isotope))
    back_button.config(width=get_width(["Back"]))
    back_button.pack(pady=5)

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