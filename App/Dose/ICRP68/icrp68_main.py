##### IMPORTS #####
import tkinter as tk
from tkinter import ttk
from App.style import SectionFrame
from App.scroll import scroll_to_top
from Utility.Functions.logic_utility import get_item, valid_saved
from Core.Dose.ICRP68.icrp68_calculations import handle_calculation
from Utility.Functions.choices import get_choices, get_icrp_isotopes, read_dose_columns
from Utility.Functions.gui_utility import (
    make_spacer, get_width,
    basic_label, result_label,
    make_title_frame, make_result_box,
    make_exit_button, make_advanced_button,
    make_dropdown, make_category_dropdown, make_item_dropdown
)

# For global access to nodes on ICRP68 main screen
main_list = []

#####################################################################################
# MENU SECTION
#####################################################################################

"""
This function sets up the ICRP68 main screen.
The following sections and widgets are created:
   Module Title (ICRP68 Coefficients)
   Select Intake Mode section
   Select Nuclide section
   Result section (title dependent on Calculation Mode)
   Advanced Settings button
   Exit button
This function contains all of the logic involving these widgets'
behaviors.
The sections and widgets are stored in main_list so they can be
accessed later by clear_main.
"""
def icrp68_main(root, category="Common Elements", mode="Ingestion",
                coefficient="Half Life", common_el="Ag", element="Ac", isotope=None):
    global main_list

    # Makes title frame
    title_frame = make_title_frame(root, "ICRP68 Coefficients", "Dose/ICRP68")

    # Gets the element options
    choices = get_choices(category, "Dose", "ICRP68")

    # Gets common elements
    common_elements = get_choices("Common Elements", "Dose", "ICRP68")

    # Make sure common element is a valid selection
    common_el = valid_saved(common_el, common_elements)

    # Stores mode and sets default
    var_mode = tk.StringVar(root)
    var_mode.set(mode)

    # Frame for mode input
    mode_frame = SectionFrame(root, title="Select Intake Mode")
    mode_frame.pack()
    inner_mode_frame = mode_frame.get_inner_frame()

    # Logic for when an Intake Mode is selected
    def select_mode(event):
        nonlocal mode
        event.widget.selection_clear()

        # Update mode variable and fixes result section title
        mode = var_mode.get()
        result_frame.change_title(mode)

        # Clear result label
        result_box.config(state="normal")
        result_box.delete("1.0", tk.END)
        result_box.config(state="disabled", height=1)

        root.focus()

    # Creates dropdown menu for mode
    mode_choices = ["Ingestion",
                    "Inhalation"]
    _ = make_dropdown(inner_mode_frame, var_mode, mode_choices, select_mode, pady=20)

    # Spacer
    empty_frame1 = make_spacer(root)

    # Creates list of coefficients
    coefficient_choices = []
    read_dose_columns(coefficient_choices, "ICRP68")

    # Frame for coefficient selection
    coefficient_frame = SectionFrame(root, title="Select Coefficient")
    coefficient_frame.pack()
    inner_coefficient_frame = coefficient_frame.get_inner_frame()

    # Stores coefficient and sets default
    var_coefficient = tk.StringVar(root)
    var_coefficient.set(coefficient)

    # Logic for when a coefficient is selected
    def on_select_coefficient(event):
        nonlocal coefficient

        event.widget.selection_clear()
        coefficient = var_coefficient.get()
        root.focus()

    # Creates dropdown menu for coefficient
    _ = make_dropdown(inner_coefficient_frame, var_coefficient, coefficient_choices,
                      on_select_coefficient, pady=20)

    # Spacer
    empty_frame2 = make_spacer(root)

    # Frame for nuclide selection
    nuclide_frame = SectionFrame(root, title="Select Nuclide")
    nuclide_frame.pack()
    inner_nuclide_frame = nuclide_frame.get_inner_frame()

    # Stores category selection and sets default
    var_category = tk.StringVar(root)
    var_category.set(category)

    # Logic for when an element category is selected
    def select_category(event):
        nonlocal choices, category, common_el, element, isotope

        event.widget.selection_clear()
        previous_element = get_item(category, common_el, "", element, "", "")
        category = var_category.get()

        # Updates element dropdown to match category
        choices = get_choices(category, "Dose", "ICRP68")
        selected_element = get_item(category, common_el, "", element, "", "")
        var_element.set(selected_element)
        element_dropdown.set_completion_list(choices)
        element_dropdown.config(values=choices, width=get_width(choices))

        # Updates isotope dropdown to match element
        isotopes = get_icrp_isotopes(selected_element, "ICRP68")
        if category == "Common Elements":
            if common_el != previous_element:
                isotope = isotopes[0]
        elif category == "All Elements":
            if element != previous_element:
                isotope = isotopes[0]
        var_isotope.set(isotope)
        isotope_dropdown.config(values=isotopes, width=get_width(isotopes))

        root.focus()

    # Frame for element category selection
    category_frame = tk.Frame(inner_nuclide_frame, bg="#F2F2F2")
    category_frame.pack(pady=(15,5))

    # Category label
    basic_label(category_frame, "Category:")

    # Creates dropdown menu for category selection
    make_category_dropdown(category_frame, var_category, select_category, False)

    # Horizontal frame for nuclide selection
    nuclide_side_frame = tk.Frame(inner_nuclide_frame, bg="#F2F2F2")
    nuclide_side_frame.pack(pady=(20,30))

    # Logic for when enter is hit when using the element autocomplete combobox
    def on_enter(_):
        nonlocal common_el, element, isotope
        value = var_element.get()

        if value not in choices:
            # Falls back on default if invalid element is typed in
            var_element.set(get_item(category, common_el, "", element, "", ""))
        else:
            # Adjusts isotopes
            isotopes = get_icrp_isotopes(value, "ICRP68")
            if category == "All Elements":
                if element != value:
                    isotope = isotopes[0]
                    element = value
            else:
                if common_el != value:
                    isotope = isotopes[0]
                    common_el = value
            var_isotope.set(isotope)
            isotope_dropdown.config(values=isotopes, width=get_width(isotopes))

        element_dropdown.selection_clear()
        element_dropdown.icursor(tk.END)

    # Logic for when an element is selected
    def on_select_element(event):
        nonlocal common_el, element, isotope

        event.widget.selection_clear()
        value = var_element.get()

        # Adjusts isotopes
        isotopes = get_icrp_isotopes(value, "ICRP68")
        if category == "All Elements":
            if element != value:
                isotope = isotopes[0]
                element = value
        else:
            if common_el != value:
                isotope = isotopes[0]
                common_el = value
        var_isotope.set(isotope)
        isotope_dropdown.config(values=isotopes, width=get_width(isotopes))

        root.focus()

    # Frame for element selection
    element_frame = tk.Frame(nuclide_side_frame, bg="#F2F2F2")
    element_frame.pack(side="left", padx=5)

    # Element label
    basic_label(element_frame, "Element:")

    # Stores element selection and sets default
    var_element = tk.StringVar(root)
    var_element.set(get_item(category, common_el, "", element, "", ""))

    # Creates dropdown menu for element
    element_dropdown = make_item_dropdown(root, element_frame, var_element,
                                          choices, on_enter, on_select_element)

    # Logic for when an isotope is selected
    def on_select_isotope(event):
        nonlocal isotope

        event.widget.selection_clear()
        isotope = var_isotope.get()
        root.focus()

    # Frame for isotope selection
    isotope_frame = tk.Frame(nuclide_side_frame, bg="#F2F2F2")
    isotope_frame.pack(side="left", padx=5)

    # Isotope label
    basic_label(isotope_frame, "Isotope:")

    # Retrieves isotopes for current element
    isotope_choices = get_icrp_isotopes(get_item(category, common_el, "", element, "", ""), "ICRP68")
    if not isotope:
        isotope = isotope_choices[0]

    # Stores isotope and sets default
    var_isotope = tk.StringVar(root)
    var_isotope.set(isotope)

    # Creates dropdown menu for isotope
    isotope_dropdown = make_dropdown(isotope_frame, var_isotope, isotope_choices,
                                     on_select_isotope)

    # Spacer
    empty_frame3 = make_spacer(root)

    # Frame for result
    result_frame = SectionFrame(root, title=mode)
    result_frame.pack()
    inner_result_frame = result_frame.get_inner_frame()

    # Creates Calculate button
    calc_button = ttk.Button(inner_result_frame, text="Calculate",
                             style="Maize.TButton", padding=(0,0),
                             command=lambda: handle_calculation(root, mode, coefficient, element,
                                                                isotope, result_box))
    calc_button.config(width=get_width(["Calculate"]))
    calc_button.pack(pady=(20,5))

    # Result label
    result_label(inner_result_frame)

    # Displays the result of calculation
    result_box = make_result_box(inner_result_frame)

    # Creates Advanced Settings button
    advanced_button = make_advanced_button(root, lambda: to_advanced(root, category, mode,
                                                                     common_el, element, isotope))

    # Creates Exit button to return to home screen
    exit_button = make_exit_button(root, lambda: exit_to_home(root))

    # Stores nodes into global list
    main_list = [title_frame,
                 mode_frame, empty_frame1,
                 coefficient_frame, empty_frame2,
                 nuclide_frame, empty_frame3,
                 result_frame, advanced_button, exit_button]

#####################################################################################
# NAVIGATION SECTION
#####################################################################################

"""
This function clears the ICRP68 main screen
in preparation for opening a different screen.
"""
def clear_main():
    global main_list

    # Clears ICRP68 main screen
    for node in main_list:
        node.destroy()
    main_list.clear()

"""
This function transitions from the ICRP68 main screen
to the home screen by first clearing the ICRP68 main screen
and then creating the home screen.
It is called when the Exit button is hit.
"""
def exit_to_home(root):
    root.focus()
    from App.home import return_home
    clear_main()
    return_home(root)
    scroll_to_top()

"""
This function transitions from the ICRP68 main screen
to the ICRP68 advanced screen by first clearing the
ICRP68 main screen and then creating the
ICRP68 advanced screen.
It is called when the Advanced Settings button is hit.
"""
def to_advanced(root, category, mode, common_el, element, isotope):
    root.focus()
    from App.Dose.ICRP68.icrp68_advanced import icrp68_advanced

    clear_main()
    icrp68_advanced(root, category, mode, common_el, element, isotope)
    scroll_to_top()