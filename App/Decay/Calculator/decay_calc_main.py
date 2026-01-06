##### IMPORTS #####
import shelve
import platform
import tkinter as tk
from tkinter import ttk
import tkinter.font as font
from App.style import SectionFrame
from App.scroll import scroll_to_top
from Utility.Functions.time import get_time
from Utility.Functions.files import get_user_data_path
from Utility.Functions.logic_utility import get_item, valid_saved
from Core.Decay.Calculator.nuclide_calc import handle_calculation
from Utility.Functions.choices import get_choices, get_isotopes, get_nuclide_vars
from Utility.Functions.gui_utility import (
    make_spacer, get_width,
    basic_label, result_label,
    make_title_frame, make_result_box,
    make_exit_button, make_advanced_button,
    make_dropdown, make_category_dropdown, make_item_dropdown
)

# For global access to nodes on decay calculator main screen
main_list = []

#####################################################################################
# MENU SECTION
#####################################################################################

"""
This function sets up the decay calculator main screen.
The following sections and widgets are created:
   Module Title (Decay Calculator)
   Select Calculation Mode section
   Select Nuclide section
   Input Details section
   Result section (title dependent on Calculation Mode)
   Exit button
This function contains all of the logic involving these widgets'
behaviors.
The sections and widgets are stored in main_list so they can be
accessed later by clear_main.
"""
def decay_calc_main(root, category="Common Elements", mode="Activities",
                    common_el="Ag", element="Ac", isotope=None, dates=False,
                    nuclide_vars=None):
    global main_list

    # Retrieves isotopes for current element
    isotope_choices = get_isotopes(get_item(category, common_el, "", element, "", ""))
    if not isotope:
        isotope = isotope_choices[0]

    # Initializes nuclide selectors if necessary
    if not nuclide_vars:
        nuclide_vars = get_nuclide_vars(isotope)

    # Gets units from user prefs
    db_path = get_user_data_path("Settings/Decay/Calculator")
    with shelve.open(db_path) as prefs:
        amount_unit = prefs.get("amount_unit", "Bq")
        time_unit = prefs.get("time_unit", "s")

    # Makes title frame
    title_frame = make_title_frame(root, "Decay Calculator", "Decay/Calculator")

    # Creates font for result label and energy entry
    monospace_font = font.Font(family="Menlo", size=12)

    # Gets the element options
    choices = get_choices(category, "Decay", "")

    # Gets common elements
    common_elements = get_choices("Common Elements", "Decay", "")

    # Make sure common element is a valid selection
    common_el = valid_saved(common_el, common_elements)

    # Stores mode and sets default
    var_mode = tk.StringVar(root)
    var_mode.set(mode)

    # Frame for mode input
    mode_frame = SectionFrame(root, title="Select Calculation Mode")
    mode_frame.pack()
    inner_mode_frame = mode_frame.get_inner_frame()

    # Logic for when a Calculation Mode is selected
    def select_mode(event):
        nonlocal mode
        event.widget.selection_clear()

        if event.widget.get() != "Plot" \
                and mode == "Plot":
            # Gets rid of save file option when switching off of decay scheme plot mode
            save.pack_forget()
        elif mode != "Plot" \
                and event.widget.get() == "Plot":
            # Reset in preparation to re-add results section in correct place
            calc_button.pack_forget()
            result.pack_forget()
            result_box.pack_forget()

            # Creates save file option when switching to decay scheme plot mode
            save.pack(pady=(20,0))

            # Re-adds everything below save file option section
            calc_button.pack(pady=(20,5))
            result.pack(pady=(5,1))
            result_box.pack(pady=(1,20))

        # Update mode variable and fixes result section title
        mode = var_mode.get()
        result_frame.change_title(mode)

        # Clear result label
        result_box.config(state="normal")
        result_box.delete("1.0", tk.END)
        result_box.config(state="disabled", height=1)

        root.focus()

    # Creates dropdown menu for mode
    mode_choices = ["Activities",
                    "Plot"]
    _ = make_dropdown(inner_mode_frame, var_mode, mode_choices, select_mode, pady=20)

    # Spacer
    empty_frame1 = make_spacer(root)

    # Frame for nuclide selection
    nuclide_frame = SectionFrame(root, title="Select Nuclide")
    nuclide_frame.pack()
    inner_nuclide_frame = nuclide_frame.get_inner_frame()

    # Stores category selection and sets default
    var_category = tk.StringVar(root)
    var_category.set(category)

    # Logic for when an element category is selected
    def select_category(event):
        nonlocal choices, category, common_el, element, isotope, nuclide_vars

        event.widget.selection_clear()
        previous_element = get_item(category, common_el, "", element, "", "")
        category = var_category.get()

        # Updates element dropdown to match category
        choices = get_choices(category, "Decay", "")
        selected_element = get_item(category, common_el, "", element, "", "")
        var_element.set(selected_element)
        element_dropdown.set_completion_list(choices)
        element_dropdown.config(values=choices, width=get_width(choices))

        # Updates isotope dropdown to match element
        isotopes = get_isotopes(selected_element)
        if category == "Common Elements":
            if common_el != previous_element:
                isotope = isotopes[0]
        elif category == "All Elements":
            if element != previous_element:
                isotope = isotopes[0]
        var_isotope.set(isotope)
        isotope_dropdown.config(values=isotopes, width=get_width(isotopes))

        # Initializes nuclide selectors
        nuclide_vars = get_nuclide_vars(isotope)

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
        nonlocal common_el, element, isotope, nuclide_vars
        value = var_element.get()

        if value not in choices:
            # Falls back on default if invalid item is typed in
            var_element.set(get_item(category, common_el, "", element, "", ""))
        else:
            # Adjusts isotopes
            isotopes = get_isotopes(value)
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

        # Initializes nuclide selectors
        nuclide_vars = get_nuclide_vars(isotope)

    # Logic for when an element is selected
    def on_select_element(event):
        nonlocal common_el, element, isotope, nuclide_vars

        event.widget.selection_clear()
        value = var_element.get()

        # Adjusts isotopes
        isotopes = get_isotopes(value)
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

        # Initializes nuclide selectors
        nuclide_vars = get_nuclide_vars(isotope)

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
        nonlocal isotope, nuclide_vars

        event.widget.selection_clear()
        isotope = var_isotope.get()
        root.focus()

        # Initializes nuclide selectors
        nuclide_vars = get_nuclide_vars(isotope)

    # Frame for isotope selection
    isotope_frame = tk.Frame(nuclide_side_frame, bg="#F2F2F2")
    isotope_frame.pack(side="left", padx=5)

    # Isotope label
    basic_label(isotope_frame, "Isotope:")

    # Stores isotope and sets default
    var_isotope = tk.StringVar(root)
    var_isotope.set(isotope)

    # Creates dropdown menu for isotope
    isotope_dropdown = make_dropdown(isotope_frame, var_isotope, isotope_choices,
                                     on_select_isotope)

    # Spacer
    empty_frame2 = make_spacer(root)

    # Input box width
    small_entry_width = 7 if platform.system() == "Windows" else 8
    entry_width = 10 if platform.system() == "Windows" else 12

    # Frame for details
    details_frame = SectionFrame(root, title="Input Details")
    details_frame.pack()
    inner_details_frame = details_frame.get_inner_frame()

    # Placeholder
    time_input = tk.Entry()
    start_date_input = tk.Entry()
    end_date_input = tk.Entry()

    if not dates:
        # Time label
        time_label = ttk.Label(inner_details_frame, text="Time Elapsed (" + time_unit + "):",
                               style="Black.TLabel")
        time_label.pack(pady=(15,1))

        # Time input
        time_input = tk.Entry(inner_details_frame, width=small_entry_width, insertbackground="black",
                              background="white", foreground="black", borderwidth=3, bd=3,
                              highlightthickness=0, relief='solid', font=monospace_font)
        time_input.pack(pady=(1,20))
    else:
        # Format label
        format_label = ttk.Label(inner_details_frame, text="Format: YYYY-MM-DD",
                                 style="Black.TLabel")
        format_label.pack(pady=(15,1))

        # Frame for dates
        date_side_frame = tk.Frame(inner_details_frame, bg="#F2F2F2")
        date_side_frame.pack(pady=20)

        # Frame for start_date
        start_date_frame = tk.Frame(date_side_frame, bg="#F2F2F2")
        start_date_frame.pack(side="left", padx=5)

        # Start date label
        start_date_label = ttk.Label(start_date_frame, text="Start Date:",
                               style="Black.TLabel")
        start_date_label.pack(pady=(0,1))

        # Start date input
        start_date_input = tk.Entry(start_date_frame, width=entry_width, insertbackground="black",
                                    background="white", foreground="black", borderwidth=3, bd=3,
                                    highlightthickness=0, relief='solid', font=monospace_font)
        start_date_input.pack(pady=(1,20))

        # Frame for end date
        end_date_frame = tk.Frame(date_side_frame, bg="#F2F2F2")
        end_date_frame.pack(side="left", padx=5)

        # End date label
        end_date_label = ttk.Label(end_date_frame, text="End Date:",
                                   style="Black.TLabel")
        end_date_label.pack(pady=(0,1))

        # End date input
        end_date_input = tk.Entry(end_date_frame, width=entry_width, insertbackground="black",
                                  background="white", foreground="black", borderwidth=3, bd=3,
                                  highlightthickness=0, relief='solid', font=monospace_font)
        end_date_input.pack(pady=(1,20))

    # Initial amount label
    initial_label = ttk.Label(inner_details_frame, text="Initial Amount (" + amount_unit + "):",
                              style="Black.TLabel")
    initial_label.pack(pady=(0,1))

    # Initial amount input
    initial_input = tk.Entry(inner_details_frame, width=small_entry_width, insertbackground="black",
                             background="white", foreground="black", borderwidth=3, bd=3,
                             highlightthickness=0, relief='solid', font=monospace_font)
    initial_input.pack(pady=(1,20))

    # Spacer
    empty_frame3 = make_spacer(root)

    # Frame for result
    result_frame = SectionFrame(root, title=mode)
    result_frame.pack()
    inner_result_frame = result_frame.get_inner_frame()

    # Stores whether file is saved and sets default
    var_save = tk.IntVar()
    var_save.set(0)

    # Creates checkbox for saving file
    save = ttk.Checkbutton(inner_result_frame, text="Save Plot", variable=var_save,
                           style="Maize.TCheckbutton", command=lambda: root.focus())

    # If we are in plot mode we create the option
    # to save or not save the plot
    if mode == "Plot":
        save.pack(pady=(20,0))

    # Creates Calculate button
    calc_button = ttk.Button(inner_result_frame, text="Calculate",
                             style="Maize.TButton", padding=(0,0),
                             command=lambda: handle_calculation(root, mode, isotope,
                                                                initial_input.get(),
            get_time(dates, time_input.get(), start_date_input.get(), end_date_input.get()),
                                                                dates, result_box,
                                                                nuclide_vars,
                                                                var_save.get()))
    calc_button.config(width=get_width(["Calculate"]))
    calc_button.pack(pady=(20,5))

    # Result label
    result = result_label(inner_result_frame)

    # Displays the result of calculation
    result_box = make_result_box(inner_result_frame)

    # Creates Advanced Settings button
    advanced_button = make_advanced_button(root, lambda: to_advanced(root, category, mode,
                                                                     common_el, element, isotope,
                                                                     dates, nuclide_vars))

    # Creates Exit button to return to home screen
    exit_button = make_exit_button(root, lambda: exit_to_home(root))

    # Stores nodes into global list
    main_list = [title_frame,
                 mode_frame, empty_frame1,
                 nuclide_frame, empty_frame2,
                 details_frame, empty_frame3,
                 result_frame, advanced_button, exit_button]


#####################################################################################
# NAVIGATION SECTION
#####################################################################################

"""
This function clears the decay calculator main screen
in preparation for opening a different screen.
"""

def clear_main():
    global main_list

    # Clears decay calculator main screen
    for node in main_list:
        node.destroy()
    main_list.clear()

"""
This function transitions from the decay calculator main screen
to the home screen by first clearing the decay calculator main screen
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
This function transitions from the decay calculator main screen
to the decay calculator advanced screen by first clearing the
decay calculator main screen and then creating the
decay calculator advanced screen.
It is called when the Advanced Settings button is hit.
"""
def to_advanced(root, category, mode, common_el, element, isotope,
                dates, nuclide_vars):
    root.focus()
    from App.Decay.Calculator.decay_calc_advanced import decay_calc_advanced

    clear_main()
    decay_calc_advanced(root, category, mode, common_el, element, isotope,
                        dates, nuclide_vars)
    scroll_to_top()