##### IMPORTS #####
import shelve
import platform
import tkinter as tk
from tkinter import ttk
import tkinter.font as font
from App.style import SectionFrame
from App.scroll import scroll_to_top
from Utility.Functions.files import get_user_data_path
from Utility.Functions.logic_utility import get_item, valid_saved
from Utility.Controllers.element_controller import update_elements
from Utility.Controllers.isotope_controller import update_isotopes
from Core.Dose.ICRP68.icrp68_calculations import handle_calculation
from Utility.Functions.choices import get_choices, get_icrp_isotopes, read_dose_columns
from Utility.Functions.gui_utility import (
    make_spacer, get_width,
    basic_label, result_label,
    make_title_frame, make_result_box,
    make_dropdown, make_category_dropdown, make_item_dropdown,
    make_exit_button, make_advanced_button, make_calculate_button
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
def icrp68_main(root, mode="Ingestion", coefficient="Half Life"):
    global main_list

    # Module directory
    module = "Dose/ICRP68"

    # Gets category, common_el, element, isotope, intake unit, and dose selector from user prefs
    db_path = get_user_data_path(f"Settings/{module}")
    with shelve.open(db_path) as prefs:
        category = prefs.get("category", "Common Elements")
        common_el = prefs.get("common_el", "Ag")

        # Gets common elements
        common_elements = get_choices("Common Elements", "Dose", "")

        # Make sure common element is a valid selection
        common_el = valid_saved(common_el, common_elements)
        prefs["common_el"] = common_el

        element = prefs.get("element", "Ac")

        # Retrieves isotopes for current element
        isotope_choices = get_icrp_isotopes(get_item(category, common_el, "", element, "", ""), "ICRP68")

        isotope = prefs.get("isotope", isotope_choices[0] if isotope_choices else "")
        intake_unit = prefs.get("intake_unit", "Bq")
        dose = prefs.get("dose", False)

    # Makes title frame
    title_frame = make_title_frame(root, "ICRP68 Coefficients", module)

    # Creates font for result label
    monospace_font = font.Font(family="Menlo", size=12)

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

        # Clear dose label
        dose_result.config(state="normal")
        dose_result.delete("1.0", tk.END)
        dose_result.config(state="disabled")

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
        nonlocal coefficient, empty_frame3, empty_frame4
        event.widget.selection_clear()

        if (event.widget.get() == "Half Life" or event.widget.get() == "f1") \
                and (coefficient != "Half Life" and coefficient != "f1"):
            # Gets rid of dose label when switching onto Half Life or f1
            dose_label.pack_forget()
            dose_result.pack_forget()
            dose_check.pack_forget()
            intake_frame.pack_forget()
            empty_frame3.pack_forget()
            coefficient_dropdown.pack(pady=20)
        elif (coefficient == "Half Life" or coefficient == "f1") \
             and (event.widget.get() != "Half Life" and event.widget.get() != "f1"):
            # Creates dose label
            coefficient_dropdown.pack(pady=(20,10))
            dose_check.pack(pady=(0,20))
            var_dose.set(dose)

            if dose:
                # Adds dose box
                dose_label.pack(pady=(5,1))
                dose_result.pack(pady=(1,20))

                # Adds intake frame
                main_list.remove(empty_frame3)
                main_list.remove(empty_frame4)
                empty_frame3.pack_forget()
                nuclide_frame.pack_forget()
                empty_frame4.pack_forget()
                result_frame.pack_forget()
                advanced_button.pack_forget()
                exit_button.pack_forget()
                intake_frame.pack()
                empty_frame3 = make_spacer(root)
                main_list.append(empty_frame3)
                nuclide_frame.pack()
                empty_frame4 = make_spacer(root)
                main_list.append(empty_frame4)
                result_frame.pack()
                advanced_button.pack(pady=5)
                exit_button.pack(pady=5)

                # Adds intake box
                intake_label.pack(pady=(15,1))
                intake_entry.pack(pady=(1,20))

        # Update coefficient variable
        coefficient = var_coefficient.get()

        # Clear result label
        result_box.config(state="normal")
        result_box.delete("1.0", tk.END)
        result_box.config(state="disabled", height=1)

        # Clear dose label
        dose_result.config(state="normal")
        dose_result.delete("1.0", tk.END)
        dose_result.config(state="disabled")

        root.focus()

    # Creates dropdown menu for coefficient
    coefficient_dropdown = make_dropdown(inner_coefficient_frame, var_coefficient, coefficient_choices,
                                         on_select_coefficient, pady=20)

    # Stores whether to find total dose for  mode
    var_dose = tk.IntVar()
    var_dose.set(int(dose))

    def dose_hit():
        nonlocal dose, empty_frame3, empty_frame4

        root.focus()
        if var_dose.get() == 1:
            # Adds dose box
            dose_label.pack(pady=(5,1))
            dose_result.pack(pady=(1,20))

            # Adds intake frame
            main_list.remove(empty_frame3)
            main_list.remove(empty_frame4)
            empty_frame3.pack_forget()
            nuclide_frame.pack_forget()
            empty_frame4.pack_forget()
            result_frame.pack_forget()
            advanced_button.pack_forget()
            exit_button.pack_forget()
            intake_frame.pack()
            empty_frame3 = make_spacer(root)
            main_list.append(empty_frame3)
            nuclide_frame.pack()
            empty_frame4 = make_spacer(root)
            main_list.append(empty_frame4)
            result_frame.pack()
            advanced_button.pack(pady=5)
            exit_button.pack(pady=5)

            # Adds intake box
            intake_label.pack(pady=(15,1))
            intake_entry.pack(pady=(1,20))
        else:
            # Forgets dose box
            dose_label.pack_forget()
            dose_result.pack_forget()

            # Forgets intake frame
            intake_frame.pack_forget()
            empty_frame3.pack_forget()

        dose = bool(var_dose.get())
        with shelve.open(db_path) as shelve_prefs:
            shelve_prefs["dose"] = dose

    # Creates checkbox for finding total dose
    dose_check = ttk.Checkbutton(inner_coefficient_frame, text="Find Total Dose?",
                                 variable=var_dose, style="Maize.TCheckbutton",
                                 command=dose_hit)

    if coefficient != "Half Life" and coefficient != "f1":
        # Displays the dose option
        coefficient_dropdown.pack(pady=(20,10))
        dose_check.pack(pady=(0,20))

    # Spacer
    empty_frame2 = make_spacer(root)

    # Frame for nuclide selection
    intake_frame = SectionFrame(root, title="Specify Intake")
    inner_intake_frame = intake_frame.get_inner_frame()

    # Input/output box width
    entry_width = 28 if platform.system() == "Windows" else 32

    # Intake label
    intake_label = ttk.Label(inner_intake_frame,
                             text=f"Intake ({intake_unit}):",
                             style="Black.TLabel")
    intake_entry = tk.Entry(inner_intake_frame, width=entry_width, insertbackground="black",
                            background="white", foreground="black", borderwidth=3, bd=3,
                            highlightthickness=0, relief='solid', font=monospace_font)

    # Spacer
    empty_frame3 = tk.Frame()

    # Only show intake frame if necessary
    if (coefficient != "Half Life" and coefficient != "f1") and dose:
        intake_frame.pack()
        intake_label.pack(pady=(15,1))
        intake_entry.pack(pady=(1,20))

        # Spacer
        empty_frame3 = make_spacer(root)

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
        with shelve.open(db_path) as shelve_prefs:
            shelve_prefs["category"] = category

        # Updates element dropdown to match category
        choices = get_choices(category, "Dose", "ICRP68")
        selected_element = get_item(category, common_el, "", element, "", "")
        var_element.set(selected_element)
        element_dropdown.set_completion_list(choices)
        element_dropdown.config(values=choices, width=get_width(choices))

        # Updates isotope dropdown to match element
        isotope = update_isotopes(category, module, selected_element, previous_element,
                                  var_isotope, isotope_dropdown, icrp="ICRP68")

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
            # Updates isotope dropdown to match element
            isotope = update_isotopes(category, module, value, value,
                                      var_isotope, isotope_dropdown, icrp="ICRP68")

            # Updates elements
            common_el, element = update_elements(category, module, value)

        element_dropdown.selection_clear()
        element_dropdown.icursor(tk.END)

    # Logic for when an element is selected
    def on_select_element(event):
        nonlocal common_el, element, isotope

        event.widget.selection_clear()
        value = var_element.get()

        # Updates isotope dropdown to match element
        isotope = update_isotopes(category, module, value, value,
                                  var_isotope, isotope_dropdown, icrp="ICRP68")

        # Updates elements
        common_el, element = update_elements(category, module, value)

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
        with shelve.open(db_path) as shelve_prefs:
            shelve_prefs["isotope"] = isotope
        root.focus()

    # Frame for isotope selection
    isotope_frame = tk.Frame(nuclide_side_frame, bg="#F2F2F2")
    isotope_frame.pack(side="left", padx=5)

    # Isotope label
    basic_label(isotope_frame, "Isotope:")

    # Retrieves isotopes for current element
    isotope_choices = get_icrp_isotopes(get_item(category, common_el, "", element, "", ""), "ICRP68")
    if not isotope:
        isotope = isotope_choices[0] if isotope_choices else ""

    # Stores isotope and sets default
    var_isotope = tk.StringVar(root)
    var_isotope.set(isotope)

    # Creates dropdown menu for isotope
    isotope_dropdown = make_dropdown(isotope_frame, var_isotope, isotope_choices,
                                     on_select_isotope)

    # Spacer
    empty_frame4 = make_spacer(root)

    # Frame for result
    result_frame = SectionFrame(root, title=mode)
    result_frame.pack()
    inner_result_frame = result_frame.get_inner_frame()

    # Creates Calculate button
    make_calculate_button(inner_result_frame, lambda: handle_calculation(root, mode, coefficient,
                                                                         intake_entry.get(),
                                                                         result_box, dose_result))

    # Result label
    result_label(inner_result_frame)

    # Displays the result of calculation
    result_box = make_result_box(inner_result_frame)

    # Creates dose result box
    dose_label = ttk.Label(inner_result_frame, text="Total Dose:",
                            style="Black.TLabel")
    dose_result = tk.Text(inner_result_frame, height=1, borderwidth=3, bd=3,
                          highlightthickness=0, relief='solid')
    dose_result.config(bg='white', fg='black', state="disabled", width=entry_width,
                       font=monospace_font)

    if (coefficient != "Half Life" and coefficient != "f1") and dose:
        # Adds dose box
        dose_label.pack(pady=(5,1))
        dose_result.pack(pady=(1,20))

    # Creates Advanced Settings button
    advanced_button = make_advanced_button(root, lambda: to_advanced(root, mode, coefficient))

    # Creates Exit button to return to home screen
    exit_button = make_exit_button(root, lambda: exit_to_home(root))

    # Stores nodes into global list
    main_list = [title_frame,
                 mode_frame, empty_frame1,
                 coefficient_frame, empty_frame2,
                 intake_frame, empty_frame3,
                 nuclide_frame, empty_frame4,
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
def to_advanced(root, mode, coefficient):
    root.focus()
    from App.Dose.ICRP68.icrp68_advanced import icrp68_advanced

    clear_main()
    icrp68_advanced(root, mode, coefficient)
    scroll_to_top()