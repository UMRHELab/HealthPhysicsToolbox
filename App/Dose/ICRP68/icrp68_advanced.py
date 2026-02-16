##### IMPORTS #####
import shelve
import tkinter as tk
from tkinter import ttk
from App.style import SectionFrame
from App.scroll import scroll_to_top
from Utility.Functions.files import get_user_data_path
from App.Dose.ICRP68.icrp68_export import icrp68_export
from Utility.Functions.files import resource_path, open_file
from Utility.Functions.gui_utility import (
    make_back_button,
    make_unit_dropdown,
    make_title_frame,
    make_spacer, get_width,
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
def icrp68_advanced(root, mode, coefficient):
    global advanced_list

    # Module directory
    module = "Dose/ICRP68"

    # Gets units from user prefs
    db_path = get_user_data_path(f"Settings/{module}")
    with shelve.open(db_path) as prefs:
        dose_type = prefs.get("dose_type", "Dose (Sv)")
        dose_unit = prefs.get("dose_unit", "Sv")
        intake_type = prefs.get("intake_type", "Intake (Bq)")
        intake_unit = prefs.get("intake_unit", "Bq")

    # Makes title frame
    title_frame = make_title_frame(root, "ICRP68 Coefficients", "Dose/ICRP68")

    # Frame for add/remove settings
    a_r_frame = make_customize_common_elements_frame(root, "Dose", "ICRP68")

    # Spacer
    empty_frame1 = make_spacer(root)

    # Frame for units
    unit_frame = SectionFrame(root, title="Select Units")
    unit_frame.pack()
    inner_unit_frame = unit_frame.get_inner_frame()

    # Horizontal frame for dose unit settings
    dose_unit_side_frame = tk.Frame(inner_unit_frame, bg="#F2F2F2")
    dose_unit_side_frame.pack(pady=20)

    # Dose unit label
    dose_unit_label = ttk.Label(dose_unit_side_frame, text="Dose Units:", style="Black.TLabel")
    dose_unit_label.pack(side='left', padx=5)

    # Logic for when a dose type is selected
    def on_select_dose_type(event):
        event.widget.selection_clear()
        selection = event.widget.get()

        with shelve.open(db_path) as shelve_prefs:
            og_dose_type = shelve_prefs.get("dose_type", "Dose (Sv)")

        # Adjusts unit choices
        unit_choices = dose_choices[selection]
        if og_dose_type != selection:
            with shelve.open(db_path) as shelve_prefs:
                shelve_prefs["dose_unit"] = default_choices[selection]
                dose_unit_dropdown.set(default_choices[selection])
                dose_unit_dropdown.config(values=unit_choices,
                                          width=get_width(unit_choices))

        with shelve.open(db_path) as shelve_prefs:
            shelve_prefs["dose_type"] = selection
        root.focus()

    # Possible dose unit types
    dose_types = ["Dose (Sv)",
                  "Dose (rem)"]

    # Stores dose type and sets default
    var_dose_type = tk.StringVar(root)
    var_dose_type.set(dose_type)

    # Creates dropdown menu for dose type
    _ = make_unit_dropdown(dose_unit_side_frame, var_dose_type, dose_types, on_select_dose_type)

    # Logic for when dose unit is selected
    def on_select_dose_unit(event):
        event.widget.selection_clear()
        root.focus()
        selection = event.widget.get()
        with shelve.open(db_path) as shelve_prefs:
            shelve_prefs["dose_unit"] = selection

    # Defaults
    default_choices = {
        "Dose (Sv)" : "Sv",
        "Dose (rem)" : "rem",
        "Intake (Bq)" : "Bq",
        "Intake (Ci)" : "Ci"
    }

    # Possible dose unit choices
    dose_choices = {
        "Dose (Sv)" : ["pSv", "nSv", "μSv", "mSv", "Sv"],
        "Dose (rem)" : ["μrem", "mrem", "rem"]
    }

    # Stores dose unit and sets default
    var_dose = tk.StringVar(root)
    var_dose.set(dose_unit)

    # Creates dropdown menu for dose unit
    dose_unit_dropdown = make_unit_dropdown(dose_unit_side_frame, var_dose,
                                            dose_choices[dose_type],
                                            on_select_dose_unit)

    # Horizontal frame for intake unit settings
    intake_unit_side_frame = tk.Frame(inner_unit_frame, bg="#F2F2F2")
    intake_unit_side_frame.pack(pady=(0,20))

    # Intake unit label
    intake_unit_label = ttk.Label(intake_unit_side_frame, text="Intake Units:", style="Black.TLabel")
    intake_unit_label.pack(side='left', padx=5)

    # Logic for when an intake type is selected
    def on_select_intake_type(event):
        event.widget.selection_clear()
        selection = event.widget.get()

        with shelve.open(db_path) as shelve_prefs:
            og_intake_type = shelve_prefs.get("intake_type", "Intake (Bq)")

        # Adjusts unit choices
        unit_choices = intake_choices[selection]
        if og_intake_type != selection:
            with shelve.open(db_path) as shelve_prefs:
                shelve_prefs["intake_unit"] = default_choices[selection]
                intake_unit_dropdown.set(default_choices[selection])
                intake_unit_dropdown.config(values=unit_choices,
                                            width=get_width(unit_choices))

        with shelve.open(db_path) as shelve_prefs:
            shelve_prefs["intake_type"] = selection
        root.focus()

    # Possible intake unit types
    intake_types = ["Intake (Bq)",
                    "Intake (Ci)"]

    # Stores intake type and sets default
    var_intake_type = tk.StringVar(root)
    var_intake_type.set(intake_type)

    # Creates dropdown menu for intake type
    _ = make_unit_dropdown(intake_unit_side_frame, var_intake_type, intake_types, on_select_intake_type)

    # Logic for when intake unit is selected
    def on_select_intake_unit(event):
        event.widget.selection_clear()
        root.focus()
        selection = event.widget.get()
        with shelve.open(db_path) as shelve_prefs:
            shelve_prefs["intake_unit"] = selection

    # Possible intake unit choices
    intake_choices = {
        "Intake (Bq)" : ["Bq", "kBq", "MBq", "GBq"],
        "Intake (Ci)" : ["pCi", "nCi", "μCi", "mCi", "Ci"]
    }

    # Stores intake unit and sets default
    var_intake = tk.StringVar(root)
    var_intake.set(intake_unit)

    # Creates dropdown menu for intake unit
    intake_unit_dropdown = make_unit_dropdown(intake_unit_side_frame, var_intake,
                                              intake_choices[intake_type],
                                              on_select_intake_unit)

    # Spacer
    empty_frame2 = make_spacer(root)

    # Frame for Export Menu, References, & Help
    bottom_frame = tk.Frame(root, bg="#F2F2F2")
    bottom_frame.pack(pady=5)

    # Creates Export Menu button
    make_export_menu_button(bottom_frame, lambda: to_export_menu(root, mode, coefficient))

    # Creates References & Help buttons
    make_references_button(bottom_frame, lambda: open_ref(root))
    make_help_button(bottom_frame, lambda: open_help(root))

    # Creates Back button to return to ICRP68 main screen
    back_button = make_back_button(root, lambda: to_main(root, mode, coefficient))

    # Stores nodes into global list
    advanced_list = [title_frame,
                     a_r_frame, empty_frame1,
                     unit_frame, empty_frame2,
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
def to_main(root, mode, coefficient):
    from App.Dose.ICRP68.icrp68_main import icrp68_main

    clear_advanced()
    icrp68_main(root, mode, coefficient)
    scroll_to_top()

"""
This function transitions from the ICRP68 advanced screen
to the ICRP68 export screen by first clearing the
ICRP68 advanced screen and then creating the
ICRP68 export screen.
It is called when the Export Menu button is hit.
"""
def to_export_menu(root, mode, coefficient):
    clear_advanced()
    icrp68_export(root, mode, coefficient)
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