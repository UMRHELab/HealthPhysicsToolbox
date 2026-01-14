##### IMPORTS #####
import shelve
import tkinter as tk
from tkinter import ttk
from App.style import SectionFrame
from App.scroll import scroll_to_top
from App.add_custom_menu import add_custom_menu
from Utility.Functions.choices import get_choices
from Utility.Functions.logic_utility import get_unit
from App.Shielding.Electrons.electrons_export import electrons_export
from Utility.Functions.files import resource_path, open_file, get_user_data_path
from Core.Shielding.Electrons.electrons_calculations import csda_numerator, csda_denominator
from Utility.Functions.math_utility import (
    energy_units,
    density_numerator, density_denominator
)
from Utility.Functions.gui_utility import (
    make_back_button,
    basic_label, make_spacer,
    make_title_frame, make_vertical_frame,
    make_export_menu_button, make_references_button, make_help_button,
    make_unit_dropdown, make_action_dropdown, make_customize_category_dropdown
)

# For global access to nodes on electron range advanced screen
advanced_list = []

#####################################################################################
# MENU SECTION
#####################################################################################

"""
This function sets up the electron range advanced screen.
The following sections and widgets are created:
   Module Title (Electron Range)
   Customize Categories section
   Select Units section
   Export Menu button
   References button
   Help button
   Back button
This function contains all of the logic involving these widgets'
behaviors.
The sections and widgets are stored in advanced_list so they can be
accessed later by clear_advanced.
"""
def electrons_advanced(root, category, mode, common_el, common_mat, element,
                       material, custom_mat, linear):
    global advanced_list

    # Gets units from user prefs
    db_path = get_user_data_path("Settings/Shielding/Electrons")
    with shelve.open(db_path) as prefs:
        csda_num = prefs.get("csda_num", "g")
        rec_num = prefs.get("rec_num", "g")
        d_num = prefs.get("d_num", "g")
        csda_den = prefs.get("csda_den", "cm\u00B2")
        rec_den = prefs.get("rec_den", "cm\u00B2")
        d_den = prefs.get("d_den", "cm\u00B3")
        energy_unit = prefs.get("energy_unit", "MeV")

    # Makes title frame
    title_frame = make_title_frame(root, "Electron Range", "Shielding/Electrons")

    # Gets common and non-common elements
    elements = get_choices("All Elements", "Shielding", "Electrons")
    common = get_choices("Common Elements", "Shielding", "Electrons")
    non_common = [element for element in elements if element not in common]

    # Gets common and non-common materials
    materials = get_choices("All Materials", "Shielding", "Electrons")
    common_m = get_choices("Common Materials", "Shielding", "Electrons")
    non_common_m = [material for material in materials if material not in common_m]

    # Gets custom materials
    custom = get_choices("Custom Materials", "Shielding", "Electrons")

    # Frame for add/remove settings
    a_r_frame = SectionFrame(root, title="Customize Categories")
    a_r_frame.pack()
    inner_a_r_frame = a_r_frame.get_inner_frame()

    # Horizontal frame for add/remove settings
    side_frame = tk.Frame(inner_a_r_frame, bg="#F2F2F2")
    side_frame.pack(pady=(15, 5))

    # Action button
    a_r_button = [ttk.Button()]

    # Simplifies calls to make_vertical_frame
    def make_v_frame():
        to_custom = lambda: to_custom_menu(root, category, mode,
                                           common_el, common_mat,
                                           element, material, custom_mat, linear)
        return make_vertical_frame(root, inner_a_r_frame, var_action.get(),
                                   var_customize_category.get(), non_common, common,
                                   non_common_m, common_m, custom, a_r_button,
                                   to_custom)

    # Logic for when an action or category is selected
    def on_select_options(event):
        nonlocal vertical_frame
        event.widget.selection_clear()
        root.focus()
        vertical_frame.destroy()
        vertical_frame = make_v_frame()

    # Frame for action selection
    action_frame = tk.Frame(side_frame, bg="#F2F2F2")
    action_frame.pack(side="left", padx=5)

    # Action label
    basic_label(action_frame, "Action:")

    # Stores action and sets default
    var_action = tk.StringVar(root)
    var_action.set("Add")

    # Creates dropdown menu for action
    _ = make_action_dropdown(action_frame, var_action, on_select_options)

    # Frame for category selection
    category_frame = tk.Frame(side_frame, bg="#F2F2F2")
    category_frame.pack(side="left", padx=5)

    # Category label
    basic_label(category_frame, "Category:")

    # Stores customize category and sets default
    var_customize_category = tk.StringVar(root)
    var_customize_category.set("Common Elements")

    # Creates dropdown menu for customize category
    _ = make_customize_category_dropdown(category_frame, var_customize_category, on_select_options)

    # Frame for specific add/remove settings
    vertical_frame = make_v_frame()

    # Spacer
    empty_frame1 = make_spacer(root)

    # Frame for units
    unit_frame = SectionFrame(root, title="Select Units")
    unit_frame.pack()
    inner_unit_frame = unit_frame.get_inner_frame()

    if mode != "Radiation Yield" and mode != "Density Effect Delta":
        # Horizontal frame for unit settings
        unit_side_frame = tk.Frame(inner_unit_frame, bg="#F2F2F2")
        unit_side_frame.pack(pady=(20,0) if mode != "Density" else 20)

        # Units label
        unit_label = ttk.Label(unit_side_frame, text=mode + " Units:", style="Black.TLabel")
        unit_label.pack(side='left', padx=5)

        # Logic for when a numerator unit is selected
        def on_select_num(event):
            event.widget.selection_clear()
            root.focus()
            selection = event.widget.get()
            with shelve.open(db_path) as shelve_prefs:
                if mode == "CSDA Range":
                    shelve_prefs["csda_num"] = selection
                elif mode == "Density":
                    shelve_prefs["d_num"] = selection
                elif mode == "Range-Energy Curve":
                    shelve_prefs["rec_num"] = selection

        # Logic for when a denominator unit is selected
        def on_select_den(event):
            event.widget.selection_clear()
            root.focus()
            selection = event.widget.get()
            with shelve.open(db_path) as shelve_prefs:
                if mode == "CSDA Range":
                    shelve_prefs["csda_den"] = selection
                elif mode == "Density":
                    shelve_prefs["d_den"] = selection
                elif mode == "Range-Energy Curve":
                    shelve_prefs["rec_den"] = selection

        # Mode choices
        mode_choices = ["CSDA Range",
                        "Range-Energy Curve",
                        "Radiation Yield",
                        "Density Effect Delta",
                        "Density"]

        # Possible unit choices
        num_choices = [csda_numerator, csda_numerator, [], [], density_numerator]
        den_choices = [csda_denominator, csda_denominator, [], [], density_denominator]

        # Stores numerator and sets default
        var_numerator = tk.StringVar(root)
        var_numerator.set(get_unit([csda_num, rec_num, "", "", d_num], mode_choices, mode))

        # Creates dropdown menu for numerator unit
        numerator_choices = list(get_unit(num_choices, mode_choices, mode).keys())
        _ = make_unit_dropdown(unit_side_frame, var_numerator, numerator_choices, on_select_num)

        # / label
        slash_label = ttk.Label(unit_side_frame, text="/", style="Black.TLabel")
        slash_label.pack(side='left')

        # Stores denominator and sets default
        var_denominator = tk.StringVar(root)
        var_denominator.set(get_unit([csda_den, rec_den, "", "", d_den], mode_choices, mode))

        # Creates dropdown menu for denominator unit
        denominator_choices = list(get_unit(den_choices, mode_choices, mode).keys())
        _ = make_unit_dropdown(unit_side_frame, var_denominator, denominator_choices, on_select_den)

    # Spacer
    empty_frame2 = make_spacer(root)

    # Frame for Export Menu, References, & Help
    bottom_frame = tk.Frame(root, bg="#F2F2F2")
    bottom_frame.pack(pady=5)

    # Energy Unit options are only created if
    # Calculation Mode is not Density
    if mode != "Density":
        # Horizontal frame for energy unit settings
        energy_unit_side_frame = tk.Frame(inner_unit_frame, bg="#F2F2F2")
        energy_unit_side_frame.pack(pady=20)

        # Energy unit label
        energy_unit_label = ttk.Label(energy_unit_side_frame, text="Energy Unit:",
                                      style="Black.TLabel")
        energy_unit_label.pack(side='left', padx=5)

        # Logic for when an energy unit is selected
        def on_select_energy(event):
            nonlocal energy_unit
            event.widget.selection_clear()
            root.focus()
            energy_unit = event.widget.get()

        # Stores energy unit and sets default
        var_energy = tk.StringVar(root)
        var_energy.set(energy_unit)

        # Creates dropdown menu for energy unit
        energy_choices = list(energy_units.keys())
        _ = make_unit_dropdown(energy_unit_side_frame, var_energy, energy_choices, on_select_energy)

        # Creates Export Menu button
        make_export_menu_button(bottom_frame, lambda: to_export_menu(root, category, mode,
                                                                     common_el, common_mat, element, material,
                                                                     custom_mat, linear))

    # Creates References & Help buttons
    make_references_button(bottom_frame, lambda: open_ref(root))
    make_help_button(bottom_frame, lambda: open_help(root))

    # Creates Back button to return to electron range main screen
    back_button = make_back_button(root, lambda: to_main(root, category, mode,
                                                         common_el, common_mat, element,
                                                         material, custom_mat, linear))

    # Stores nodes into global list
    advanced_list = [title_frame,
                     a_r_frame, a_r_button[0], empty_frame1,
                     unit_frame, empty_frame2,
                     bottom_frame, back_button]

#####################################################################################
# NAVIGATION SECTION
#####################################################################################

"""
This function clears the electron range advanced screen
in preparation for opening a different screen.
"""
def clear_advanced():
    global advanced_list

    # Clears electron range advanced screen
    for node in advanced_list:
        node.destroy()
    advanced_list.clear()

"""
This function transitions from the electron range advanced screen
to the electron range main screen by first clearing the
electron range advanced screen and then creating the
electron range main screen.
It is called when the Back button is hit.
"""
def to_main(root, category, mode, common_el, common_mat, element,
            material, custom_mat, linear):
    from App.Shielding.Electrons.electrons_main import electrons_main

    clear_advanced()
    electrons_main(root, category, mode, common_el, common_mat, element,
                   material, custom_mat, linear)
    scroll_to_top()

"""
This function transitions from the electron range advanced screen
to the add custom materials menu by first clearing the
electron range advanced screen and then creating the
add custom materials menu.
It is called when the Add Custom Materials button is hit.
"""
def to_custom_menu(root, category, mode, common_el, common_mat, element,
                   material, custom_mat, linear):
    clear_advanced()
    back = lambda: electrons_advanced(root, category, mode, common_el, common_mat, element,
                                      material, custom_mat, linear)

    # Gets density units from user prefs
    db_path = get_user_data_path("Settings/Shielding/Electrons")
    with shelve.open(db_path) as prefs:
        d_num = prefs.get("d_num", "g")
        d_den = prefs.get("d_den", "cm\u00B3")

    add_custom_menu(root, d_num, d_den, back)
    scroll_to_top()

"""
This function transitions from the electron range advanced screen
to the electron range export screen by first clearing the
electron range advanced screen and then creating the
electron range export screen.
It is called when the Export Menu button is hit.
"""
def to_export_menu(root, category, mode, common_el, common_mat, element,
                   material, custom_mat, linear):
    clear_advanced()
    electrons_export(root, category, mode, common_el, common_mat, element,
                     material, custom_mat, linear)
    scroll_to_top()

"""
This function opens the electron range References.txt file.
"""
def open_ref(root):
    root.focus()
    db_path = resource_path('Utility/Modules/Shielding/Electrons/References.txt')
    open_file(db_path)

"""
This function opens the electron range Help.txt file.
"""
def open_help(root):
    root.focus()
    db_path = resource_path('Utility/Modules/Shielding/Electrons/Help.txt')
    open_file(db_path)