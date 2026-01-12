##### IMPORTS #####
import shelve
import tkinter as tk
from tkinter import ttk
from App.style import SectionFrame
from App.scroll import scroll_to_top
from App.add_custom_menu import add_custom_menu
from Utility.Functions.choices import get_choices
from App.Shielding.Photons.photons_export import photons_export
from Utility.Functions.logic_utility import get_unit, get_interactions
from Utility.Functions.files import resource_path, open_file, get_user_data_path
from Core.Shielding.Photons.photons_calculations import (
    mac_numerator, mac_denominator,
    lac_numerator, lac_denominator
)
from Utility.Functions.math_utility import (
    energy_units,
    density_numerator, density_denominator
)
from Utility.Functions.gui_utility import (
    basic_label,
    make_back_button,
    interaction_checkbox,
    make_spacer, get_width,
    make_title_frame, make_vertical_frame,
    make_unit_dropdown, make_action_dropdown, make_customize_category_dropdown
)

# For global access to nodes on photon attenuation advanced screen
advanced_list = []

#####################################################################################
# MENU SECTION
#####################################################################################

"""
This function sets up the photon attenuation advanced screen.
The following sections and widgets are created:
   Module Title (Photon Attenuation)
   Customize Categories section
   Select Interaction Types section (only when Calculation Mode is not Density)
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
def photons_advanced(root, category, mode, interactions, common_el, common_mat,
                     element, material, custom_mat):
    global advanced_list

    # Gets units from user prefs
    db_path = get_user_data_path("Settings/Shielding/Photons")
    with shelve.open(db_path) as prefs:
        mac_num = prefs.get("mac_num", "cm\u00B2")
        d_num = prefs.get("d_num", "g")
        lac_num = prefs.get("lac_num", "1")
        mac_den = prefs.get("mac_den", "g")
        d_den = prefs.get("d_den", "cm\u00B3")
        lac_den = prefs.get("lac_den", "cm")
        energy_unit = prefs.get("energy_unit", "MeV")

    # Makes title frame
    title_frame = make_title_frame(root, "Photon Attenuation", "Shielding/Photons")

    # Gets common and non-common elements
    elements = get_choices("All Elements", "Shielding", "Photons")
    common = get_choices("Common Elements", "Shielding", "Photons")
    non_common = [element for element in elements if element not in common]

    # Gets common and non-common materials
    materials = get_choices("All Materials", "Shielding", "Photons")
    common_m = get_choices("Common Materials", "Shielding", "Photons")
    non_common_m = [material for material in materials if material not in common_m]

    # Gets custom materials
    custom = get_choices("Custom Materials", "Shielding", "Photons")

    # Frame for add/remove settings
    a_r_frame = SectionFrame(root, title="Customize Categories")
    a_r_frame.pack()
    inner_a_r_frame = a_r_frame.get_inner_frame()

    # Horizontal frame for add/remove settings
    side_frame = tk.Frame(inner_a_r_frame, bg="#F2F2F2")
    side_frame.pack(pady=(15,5))

    # Action button
    a_r_button = [ttk.Button()]

    # List of interactions
    interaction_choices = ["Total Attenuation with Coherent Scattering",
                           "Total Attenuation without Coherent Scattering",
                           "Pair Production in Electron Field",
                           "Pair Production in Nuclear Field",
                           "Scattering - Incoherent",
                           "Scattering - Coherent",
                           "Photo-Electric Absorption"]

    # Variables for each interaction type
    var0 = tk.IntVar()
    var1 = tk.IntVar()
    var2 = tk.IntVar()
    var3 = tk.IntVar()
    var4 = tk.IntVar()
    var5 = tk.IntVar()
    var6 = tk.IntVar()
    interaction_vars = [var0, var1, var2, var3, var4, var5, var6]

    # Selects the previously selected interactions
    for i in range(len(interaction_choices)):
        if interaction_choices[i] in interactions:
            interaction_vars[i].set(1)

    # Simplifies calls to make_vertical_frame
    def make_v_frame():
        to_custom = lambda: to_custom_menu(root, category, mode,
                                get_interactions(interaction_choices, interaction_vars),
                                           common_el, common_mat,
                                           element, material, custom_mat)
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

    # Frame for interaction type
    interactions_frame = SectionFrame(root, title="Select Interaction Types")
    inner_interactions_frame = interactions_frame.get_inner_frame()
    inner_interactions_frame.config(pady=10)

    # Spacer
    empty_frame2 = tk.Frame()

    # Ensures at least one interaction type is selected
    # If user tries to select none,
    # Total Attenuation with Coherent Scattering
    # is automatically selected
    def set_default():
        safe = False
        for var in interaction_vars:
            if var.get() == 1:
                safe = True
        if not safe:
            var0.set(1)

    # Logic for when Total Attenuation with Coherent Scattering is selected
    def on_select_total_with():
        root.focus()
        if var0.get() == 1:
            for var in interaction_vars:
                if var != var0:
                    var.set(0)
        else:
            set_default()

    # Logic for when Total Attenuation without Coherent Scattering is selected
    def on_select_total_without():
        root.focus()
        if var1.get() == 1:
            for var in interaction_vars:
                if var != var1 and var != var5:
                    var.set(0)
        else:
            set_default()

    # Logic for when Scattering - Coherent is selected
    def on_select_coherent_scattering():
        root.focus()
        if var5.get() == 1:
            var0.set(0)
        else:
            set_default()

    # Logic for when any other interaction is selected
    def on_select(var):
        root.focus()
        if var.get() == 1:
            var0.set(0)
            var1.set(0)
        else:
            set_default()

    # Select Interaction Types section is only created if
    # Calculation Mode is not Density
    if mode != "Density":
        interactions_frame.pack()

        checks = tk.Frame(inner_interactions_frame, bg="#F2F2F2")
        checks.pack()

        # Checkboxes for each interaction type
        interaction_checkbox(checks, var0,
                             "Total Attenuation with Coherent Scattering",
                             on_select_total_with)
        interaction_checkbox(checks, var1,
                             "Total Attenuation without Coherent Scattering",
                             on_select_total_without)
        interaction_checkbox(checks, var2,
                             "Pair Production in Electron Field", lambda: on_select(var2))
        interaction_checkbox(checks, var3,
                             "Pair Production in Nuclear Field", lambda: on_select(var3))
        interaction_checkbox(checks, var4,
                             "Scattering - Incoherent", lambda: on_select(var4))
        interaction_checkbox(checks, var5,
                             "Scattering - Coherent", on_select_coherent_scattering)
        interaction_checkbox(checks, var6,
                             "Photo-Electric Absorption", lambda: on_select(var6))

        # Spacer
        empty_frame2 = make_spacer(root)

    # Frame for units
    unit_frame = SectionFrame(root, title="Select Units")
    unit_frame.pack()
    inner_unit_frame = unit_frame.get_inner_frame()

    # Horizontal frame for unit settings
    unit_side_frame = tk.Frame(inner_unit_frame, bg="#F2F2F2")
    unit_side_frame.pack(pady=20)

    # Units label
    unit_label = ttk.Label(unit_side_frame, text=mode+" Units:", style="Black.TLabel")
    unit_label.pack(side='left', padx=5)

    # Logic for when a numerator unit is selected
    def on_select_num(event):
        event.widget.selection_clear()
        root.focus()
        selection = event.widget.get()
        with shelve.open(db_path) as shelve_prefs:
            if mode == "Mass Attenuation Coefficient":
                shelve_prefs["mac_num"] = selection
            elif mode == "Density":
                shelve_prefs["d_num"] = selection
            else:
                shelve_prefs["lac_num"] = selection

    # Logic for when a denominator unit is selected
    def on_select_den(event):
        event.widget.selection_clear()
        root.focus()
        selection = event.widget.get()
        with shelve.open(db_path) as shelve_prefs:
            if mode == "Mass Attenuation Coefficient":
                shelve_prefs["mac_den"] = selection
            elif mode == "Density":
                shelve_prefs["d_den"] = selection
            else:
                shelve_prefs["lac_den"] = selection

    # Mode choices
    mode_choices = ["Mass Attenuation Coefficient",
                    "Density",
                    "Linear Attenuation Coefficient"]

    # Possible unit choices
    num_choices = [mac_numerator, density_numerator, lac_numerator]
    den_choices = [mac_denominator, density_denominator, lac_denominator]

    # Stores numerator and sets default
    var_numerator = tk.StringVar(root)
    var_numerator.set(get_unit([mac_num, d_num, lac_num], mode_choices, mode))

    # Creates dropdown menu for numerator unit
    numerator_choices = list(get_unit(num_choices, mode_choices, mode).keys())
    _ = make_unit_dropdown(unit_side_frame, var_numerator, numerator_choices, on_select_num)

    # / label
    slash_label = ttk.Label(unit_side_frame, text="/", style="Black.TLabel")
    slash_label.pack(side='left')

    # Stores denominator and sets default
    var_denominator = tk.StringVar(root)
    var_denominator.set(get_unit([mac_den, d_den, lac_den], mode_choices, mode))

    # Creates dropdown menu for denominator unit
    denominator_choices = list(get_unit(den_choices, mode_choices, mode).keys())
    _ = make_unit_dropdown(unit_side_frame, var_denominator, denominator_choices, on_select_den)

    # Spacer
    empty_frame3 = make_spacer(root)

    # Frame for Export Menu, References, & Help
    bottom_frame = tk.Frame(root, bg="#F2F2F2")
    bottom_frame.pack(pady=5)

    # Energy Unit options are only created if
    # Calculation Mode is not Density
    if mode != "Density":
        # Horizontal frame for energy unit settings
        energy_unit_side_frame = tk.Frame(inner_unit_frame, bg="#F2F2F2")
        energy_unit_side_frame.pack(pady=(0,20))

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
        export_button = ttk.Button(bottom_frame, text="Export Menu", style="Maize.TButton",
                                   padding=(0,0),
                                   command=lambda:
                                   to_export_menu(root, category, mode,
                                   get_interactions(interaction_choices, interaction_vars),
                                                  common_el, common_mat, element, material,
                                                  custom_mat))
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

    # Creates Back button to return to photon attenuation main screen
    back_button = make_back_button(root, lambda: to_main(root, category, mode,
                                                get_interactions(interaction_choices, interaction_vars),
                                                         common_el, common_mat,
                                                         element, material, custom_mat))

    # Stores nodes into global list
    advanced_list = [title_frame,
                     a_r_frame, a_r_button[0], empty_frame1,
                     interactions_frame, empty_frame2,
                     unit_frame, empty_frame3,
                     bottom_frame, back_button]

#####################################################################################
# NAVIGATION SECTION
#####################################################################################

"""
This function clears the photon attenuation advanced screen
in preparation for opening a different screen.
"""
def clear_advanced():
    global advanced_list

    # Clears photon attenuation advanced screen
    for node in advanced_list:
        node.destroy()
    advanced_list.clear()

"""
This function transitions from the photon attenuation advanced screen
to the photon attenuation main screen by first clearing the
photon attenuation advanced screen and then creating the
photon attenuation main screen.
It is called when the Back button is hit.
"""
def to_main(root, category, mode, interactions, common_el, common_mat,
            element, material, custom_mat):
    from App.Shielding.Photons.photons_main import photons_main

    clear_advanced()
    photons_main(root, category, mode, interactions, common_el, common_mat,
                 element, material, custom_mat)
    scroll_to_top()

"""
This function transitions from the photon attenuation advanced screen
to the add custom materials menu by first clearing the
photon attenuation advanced screen and then creating the
add custom materials menu.
It is called when the Add Custom Materials button is hit.
"""
def to_custom_menu(root, category, mode, interactions, common_el, common_mat,
                   element, material, custom_mat):
    clear_advanced()
    back = lambda: photons_advanced(root, category, mode, interactions, common_el, common_mat,
                                    element, material, custom_mat)

    # Gets density units from user prefs
    db_path = get_user_data_path("Settings/Shielding/Photons")
    with shelve.open(db_path) as prefs:
        d_num = prefs.get("d_num", "g")
        d_den = prefs.get("d_den", "cm\u00B3")

    add_custom_menu(root, d_num, d_den, back)
    scroll_to_top()

"""
This function transitions from the photon attenuation advanced screen
to the photon attenuation export screen by first clearing the
photon attenuation advanced screen and then creating the
photon attenuation export screen.
It is called when the Export Menu button is hit.
"""
def to_export_menu(root, category, mode, interactions, common_el, common_mat,
                   element, material, custom_mat):
    clear_advanced()
    photons_export(root, category, mode, interactions, common_el, common_mat,
                   element, material, custom_mat)
    scroll_to_top()

"""
This function opens the photon attenuation References.txt file.
"""
def open_ref(root):
    root.focus()
    db_path = resource_path('Utility/Modules/Shielding/Photons/References.txt')
    open_file(db_path)

"""
This function opens the photon attenuation Help.txt file.
"""
def open_help(root):
    root.focus()
    db_path = resource_path('Utility/Modules/Shielding/Photons/Help.txt')
    open_file(db_path)