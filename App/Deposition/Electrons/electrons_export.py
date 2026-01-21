##### IMPORTS #####
import tkinter as tk
from tkinter import ttk
from App.style import SectionFrame
from App.scroll import scroll_to_top
from Core.Deposition.Electrons.electrons_plots import export_data
from Utility.Functions.logic_utility import get_item, get_interactions
from Utility.Functions.gui_utility import (
    make_title_frame,
    basic_label, make_spacer,
    make_back_button, make_export_button,
    make_export_dropdown, interaction_checkbox
)

# For global access to nodes on electron stopping power export screen
export_list = []

#####################################################################################
# MENU SECTION
#####################################################################################

"""
This function sets up the electron stopping power export screen.
The following sections and widgets are created:
   Module Title (Electron Stopping Power)
   Select Interaction Types section
   Export Options section
   Back button
This function contains all of the logic involving these widgets'
behaviors.
The sections and widgets are stored in export_list so they can be
accessed later by clear_export.
"""
def electrons_export(root, category, mode, interactions, common_el, common_mat,
                     element, material, custom_mat):
    global export_list

    # Makes title frame
    title_frame = make_title_frame(root, "Electron Stopping Power", "Deposition/Electrons")

    # Select Interaction Types frame
    interactions_frame = tk.Frame()

    # Spacer
    empty_frame1 = tk.Frame()

    # List of interactions
    interaction_choices = ["Stopping Power - Total",
                           "Stopping Power - Collision",
                           "Stopping Power - Radiative"]

    # Variables for each interaction type
    interaction_vars = [tk.IntVar() for _ in range(len(interaction_choices))]

    if mode == "Mass Stopping Power":
        # Frame for interactions
        interactions_frame = SectionFrame(root, title="Select Interaction Types")
        interactions_frame.pack()
        inner_interactions_frame = interactions_frame.get_inner_frame()
        inner_interactions_frame.config(pady=10)

        # Logic for when an interaction type is selected
        on_select = lambda: root.focus()

        # Frame for interaction checkboxes
        checks = tk.Frame(inner_interactions_frame, bg="#F2F2F2")
        checks.pack()

        # Checkboxes for each interaction type
        for index, interaction in enumerate(interaction_choices):
            interaction_checkbox(checks, interaction_vars[index], interaction, on_select)

        # Spacer
        empty_frame1 = make_spacer(root)

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
    make_export_button(inner_options_frame, lambda: export_data(root, get_item(category, common_el, common_mat,
                                                                               element, material, custom_mat),
                                                                category, mode,
                                                                get_interactions(interaction_choices, interaction_vars),
                                                                var_export.get(), var_save.get(), error_label),
                       pady=(10,5))

    # Creates error label for bad input
    error_label = ttk.Label(inner_options_frame, text="", style="Error.TLabel")
    error_label.pack(pady=(5,10))

    # Creates Back button to return to electron stopping power advanced screen
    back_button = make_back_button(root, lambda: advanced_back(root, category, mode, interactions,
                                                               common_el, common_mat, element,
                                                               material, custom_mat))

    # Stores nodes into global list
    export_list = [title_frame,
                   interactions_frame, empty_frame1,
                   options_frame, back_button]

#####################################################################################
# NAVIGATION SECTION
#####################################################################################

"""
This function clears the electron stopping power export screen
in preparation for opening a different screen.
"""
def clear_export():
    global export_list

    # Clears electron stopping power export screen
    for node in export_list:
        node.destroy()
    export_list.clear()

"""
This function transitions from the electron stopping power export screen
to the electron stopping power advanced screen by first clearing the
electron stopping power export screen and then creating the
electron stopping power advanced screen.
It is called when the Back button is hit.
"""
def advanced_back(root, category, mode, interactions, common_el, common_mat,
                  element, material, custom_mat):
    from App.Deposition.Electrons.electrons_advanced import electrons_advanced

    clear_export()
    electrons_advanced(root, category, mode, interactions, common_el, common_mat,
                       element, material, custom_mat)
    scroll_to_top()