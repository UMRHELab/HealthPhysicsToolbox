##### IMPORTS #####
import tkinter as tk
from tkinter import ttk
from App.style import SectionFrame
from Utility.Functions.logic_utility import get_item
from Core.Deposition.Photons.photons_plots import export_data
from Utility.Functions.gui_utility import make_title_frame, basic_label
from Utility.Functions.gui_utility import get_width, make_export_dropdown

# For global access to nodes on photon energy absorption export screen
export_list = []

#####################################################################################
# MENU SECTION
#####################################################################################

"""
This function sets up the photon energy absorption export screen.
The following sections and widgets are created:
   Module Title (Photon Energy Absorption)
   Select Interaction Types section
   Export Options section
   Back button
This function contains all of the logic involving these widgets'
behaviors.
The sections and widgets are stored in export_list so they can be
accessed later by clear_export.
"""
def photons_export(root, category, mode, common_el, common_mat, element,
                   material, custom_mat):
    global export_list

    # Makes title frame
    title_frame = make_title_frame(root, "Photon Energy Absorption", "Deposition/Photons")

    # Stores whether file is saved and sets default
    var_save = tk.IntVar()
    var_save.set(1)

    # Frame for options
    options_frame = SectionFrame(root, title="Export Options")
    options_frame.pack()
    inner_options_frame = options_frame.get_inner_frame()

    # Creates checkbox for saving file
    save = ttk.Checkbutton(inner_options_frame, text="Save File", variable=var_save,
                           style="Maize.TCheckbutton", command=lambda: root.focus())
    save.pack(pady=(10,5))

    # Frame for export type
    export_type_frame = tk.Frame(inner_options_frame, bg="#F2F2F2")
    export_type_frame.pack(pady=5)

    # Export label
    basic_label(export_type_frame, "Export Type:")

    # Logic for when an export type is selected
    def on_select_export(event):
        nonlocal var_save
        event.widget.selection_clear()
        root.focus()
        if event.widget.get() == "Data":
            # Forces user to save file if export type is Data
            var_save.set(1)
            save.config(state="disabled")
        else:
            save.config(state="normal")

    # Stores export type and sets default
    var_export = tk.StringVar(root)
    var_export.set("Plot")

    # Creates dropdown menu for export type
    _ = make_export_dropdown(export_type_frame, var_export, on_select_export)

    # Creates Export button
    export_button = ttk.Button(inner_options_frame, text="Export", style="Maize.TButton",
                               padding=(0,0),
                               command=lambda:
                               export_data(root,
                               get_item(category, common_el, common_mat,
                                        element, material, custom_mat),
                                           category, mode, var_export.get(),
                                           var_save.get(), error_label))
    export_button.config(width=get_width(["Export"]))
    export_button.pack(pady=(10,5))

    # Creates error label for bad input
    error_label = ttk.Label(inner_options_frame, text="", style="Error.TLabel")
    error_label.pack(pady=(5,10))

    # Creates Back button to return to photon energy absorption advanced screen
    back_button = ttk.Button(root, text="Back", style="Maize.TButton", padding=(0,0),
                             command=lambda: advanced_back(root, category, mode,
                                                           common_el, common_mat,
                                                           element, material,
                                                           custom_mat))
    back_button.config(width=get_width(["Back"]))
    back_button.pack(pady=5)

    # Stores nodes into global list
    export_list = [title_frame,
                   options_frame, back_button]

#####################################################################################
# NAVIGATION SECTION
#####################################################################################

"""
This function clears the photon energy absorption export screen
in preparation for opening a different screen.
"""
def clear_export():
    global export_list

    # Clears photon energy absorption export screen
    for node in export_list:
        node.destroy()
    export_list.clear()

"""
This function transitions from the photon energy absorption export screen
to the photon energy absorption advanced screen by first clearing the
photon energy absorption export screen and then creating the
photon energy absorption advanced screen.
It is called when the Back button is hit.
"""
def advanced_back(root, category, mode, common_el, common_mat, element,
                  material, custom_mat):
    from App.Deposition.Photons.photons_advanced import photons_advanced

    clear_export()
    photons_advanced(root, category, mode, common_el, common_mat, element,
                     material, custom_mat)