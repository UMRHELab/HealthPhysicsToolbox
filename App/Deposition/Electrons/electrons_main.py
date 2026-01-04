##### IMPORTS #####
import shelve
import platform
import tkinter as tk
from tkinter import ttk
import tkinter.font as font
from App.style import SectionFrame
from Utility.Functions.choices import get_choices
from Utility.Functions.files import get_user_data_path
from Utility.Functions.gui_utility import make_exit_button
from Utility.Functions.gui_utility import make_spacer, get_width
from Utility.Functions.logic_utility import get_item, valid_saved
from Utility.Functions.gui_utility import make_dropdown, make_result_box
from Core.Deposition.Electrons.electrons_calculations import handle_calculation
from Utility.Functions.gui_utility import make_category_dropdown, make_item_dropdown
from Utility.Functions.gui_utility import basic_label, result_label, make_title_frame

# For global access to nodes on electron stopping power main screen
main_list = []

#####################################################################################
# MENU SECTION
#####################################################################################

"""
This function sets up the electron stopping power main screen.
The following sections and widgets are created:
   Module Title (Electron Stopping Power)
   Select Calculation Mode section
   Select Interacting Medium section
   Input Energy section (only when Calculation Mode is not Density)
   Result section (title dependent on Calculation Mode)
   Advanced Settings button
   Exit button
This function contains all of the logic involving these widgets'
behaviors.
The sections and widgets are stored in main_list so they can be
accessed later by clear_main.
"""
def electrons_main(root, category="Common Elements",
                   mode="Mass Stopping Power", interactions=None, common_el="Ag",
                   common_mat="Air (dry, near sea level)", element="Ac",
                   material="A-150 Tissue-Equivalent Plastic (A150TEP)",
                   custom_mat="", linear=False):
    global main_list

    # Gets energy unit from user prefs
    db_path = get_user_data_path("Settings/Deposition/Electrons")
    with shelve.open(db_path) as prefs:
        energy_unit = prefs.get("energy_unit", "MeV")

    # Sets default interaction - Stopping Power - Total
    if mode == "Mass Stopping Power" and (interactions is None or not interactions):
        interactions = ["Stopping Power - Total"]

    # Makes title frame
    title_frame = make_title_frame(root, "Electron Stopping Power", "Deposition/Electrons")

    # Creates font for result label and energy entry
    monospace_font = font.Font(family="Menlo", size=12)

    # Gets the item options
    choices = get_choices(category, "Deposition", "Electrons")

    # Gets customizable categories
    common_elements = get_choices("Common Elements", "Deposition", "Electrons")
    common_materials = get_choices("Common Materials", "Deposition", "Electrons")
    custom_materials = get_choices("Custom Materials", "Deposition", "Electrons")

    # Make sure default choices are valid selections
    common_el = valid_saved(common_el, common_elements)
    common_mat = valid_saved(common_mat, common_materials)
    custom_mat = valid_saved(custom_mat, custom_materials)

    # Stores mode and sets default
    var_mode = tk.StringVar(root)
    var_mode.set(mode)

    # Frame for mode input
    mode_frame = SectionFrame(root, title="Select Calculation Mode")
    mode_frame.pack()
    inner_mode_frame = mode_frame.get_inner_frame()

    # Logic for when a Calculation Mode is selected
    def select_mode(event):
        nonlocal mode, empty_frame3
        event.widget.selection_clear()

        if event.widget.get() != "Mass Stopping Power" \
                and mode == "Mass Stopping Power":
            # Gets rid of result label when switching off Mass Stopping Power mode
            range_label.pack_forget()
            range_result.pack_forget()
            range_check.pack_forget()
            mode_dropdown.pack(pady=20)
        elif mode != "Mass Stopping Power" \
             and event.widget.get() == "Mass Stopping Power":
            # Creates range label
            mode_dropdown.pack(pady=(20,10))
            range_check.pack(pady=(0,20))
            var_range.set(linear)

            if linear:
                # Adds range box
                range_label.pack(pady=(5,1))
                range_result.pack(pady=(1,20))

        if event.widget.get() == "Density" \
                and mode != "Density":
            # Gets rid of input energy section when switching to density mode
            energy_frame.pack_forget()
            empty_frame3.pack_forget()
        elif mode == "Density" \
                and event.widget.get() != "Density":
            # Reset in preparation to re-add input energy section in correct place
            main_list.remove(empty_frame3)
            energy_frame.pack_forget()
            result_frame.pack_forget()
            advanced_button.pack_forget()
            exit_button.pack_forget()

            # Creates input energy section when switching away from density mode
            energy_frame.pack()
            energy_label.pack(pady=(15,1))
            energy_entry.pack(pady=(1,20))

            # Spacer
            empty_frame3 = make_spacer(root)
            main_list.append(empty_frame3)

            # Re-adds everything below input energy section
            result_frame.pack()
            advanced_button.pack(pady=5)
            exit_button.pack(pady=5)

        # Update mode variable and fixes result section title
        mode = var_mode.get()
        result_frame.change_title(mode)

        # Clear result label
        result_box.config(state="normal")
        result_box.delete("1.0", tk.END)
        result_box.config(state="disabled")

        # Clear range label
        range_result.config(state="normal")
        range_result.delete("1.0", tk.END)
        range_result.config(state="disabled")

        root.focus()

    # Creates dropdown menu for mode
    mode_choices = ["Mass Stopping Power",
                    "Radiation Yield",
                    "Density Effect Delta",
                    "Density"]
    mode_dropdown = make_dropdown(inner_mode_frame, var_mode, mode_choices, select_mode,
                                  pady=20)

    # Stores whether to find linear stopping power for Mass Stopping Power mode
    var_range = tk.IntVar()
    var_range.set(int(linear))

    def range_hit():
        nonlocal linear

        root.focus()
        if var_range.get() == 1:
            # Adds range box
            range_label.pack(pady=(5,1))
            range_result.pack(pady=(1,20))
        else:
            # Forgets range box
            range_label.pack_forget()
            range_result.pack_forget()

        linear = bool(var_range.get())

    # Creates checkbox for finding range
    range_check = ttk.Checkbutton(inner_mode_frame, text="Find Linear Stopping Power?",
                                  variable=var_range, style="Maize.TCheckbutton",
                                  command=lambda: range_hit())

    if mode == "Mass Stopping Power":
        # Displays the range option
        mode_dropdown.pack(pady=(20,10))
        range_check.pack(pady=(0,20))

    # Spacer
    empty_frame1 = make_spacer(root)

    # Stores category selection and sets default
    var_category = tk.StringVar(root)
    var_category.set(category)

    # Stores item selection and sets default
    var = tk.StringVar(root)
    var.set(get_item(category, common_el, common_mat, element, material, custom_mat))

    # Frame for interacting medium category and item
    main_frame = SectionFrame(root, title="Select Interacting Medium")
    main_frame.pack()
    inner_main_frame = main_frame.get_inner_frame()

    # Logic for when an interacting medium category is selected
    def select_category(event):
        nonlocal choices, category

        event.widget.selection_clear()
        category = var_category.get()

        # Updates item dropdown to match category
        choices = get_choices(category, "Deposition", "Electrons")
        var.set(get_item(category, common_el, common_mat, element, material, custom_mat))
        item_dropdown.set_completion_list(choices)
        item_dropdown.config(values=choices, width=get_width(choices))
        root.focus()

    # Frame for interacting medium category selection
    category_frame = tk.Frame(inner_main_frame, bg="#F2F2F2")
    category_frame.pack(pady=(15,5))

    # Category label
    basic_label(category_frame, "Category:")

    # Creates dropdown menu for category selection
    make_category_dropdown(category_frame, var_category, select_category)

    # Logic for when enter is hit when using the item autocomplete combobox
    def on_enter(_):
        nonlocal common_el, common_mat, element, material, custom_mat
        value = item_dropdown.get()
        if value not in choices:
            # Falls back on default if invalid item is typed in
            item_dropdown.set(get_item(category, common_el, common_mat,
                                       element, material, custom_mat))
        else:
            # Stores most recent items
            if category == "Common Elements":
                common_el = var.get()
            elif category == "All Elements":
                element = var.get()
            elif category == "Common Materials":
                common_mat = var.get()
            elif category == "All Materials":
                material = var.get()
            elif category == "Custom Materials":
                custom_mat = var.get()

        item_dropdown.selection_clear()
        item_dropdown.icursor(tk.END)

    # Frame for interacting medium item selection
    item_frame = tk.Frame(inner_main_frame, bg="#F2F2F2")
    item_frame.pack(pady=(5,20))

    # Item label
    basic_label(item_frame, "Item:")

    # Creates dropdown menu for interacting medium item selection
    item_dropdown = make_item_dropdown(root, item_frame, var, choices, on_enter)

    # Spacer
    empty_frame2 = make_spacer(root)

    # Frame for energy input
    energy_frame = SectionFrame(root, title="Input Energy")
    inner_energy_frame = energy_frame.get_inner_frame()

    # Input/output box width
    entry_width = 28 if platform.system() == "Windows" else 32

    # Energy label
    energy_label = ttk.Label(inner_energy_frame, text="Electron Energy (" + energy_unit + "):",
                             style="Black.TLabel")
    energy_entry = tk.Entry(inner_energy_frame, width=entry_width, insertbackground="black",
                            background="white", foreground="black", borderwidth=3, bd=3,
                            highlightthickness=0, relief='solid', font=monospace_font)

    empty_frame3 = tk.Frame()

    # Input Energy section is created if Calculation Mode is not Density
    if mode != "Density":
        energy_frame.pack()
        energy_label.pack(pady=(15,1))
        energy_entry.pack(pady=(1,20))

        # Spacer
        empty_frame3 = make_spacer(root)

    # Frame for result
    result_frame = SectionFrame(root, title=mode)
    result_frame.pack()
    inner_result_frame = result_frame.get_inner_frame()

    # Creates Calculate button
    calc_button = ttk.Button(inner_result_frame, text="Calculate",
                             style="Maize.TButton", padding=(0,0),
                             command=lambda: handle_calculation(root, category,
                                                                mode, interactions, var.get(),
                                                                energy_entry.get(),
                                                                result_box, range_result))
    calc_button.config(width=get_width(["Calculate"]))
    calc_button.pack(pady=(20,5))

    # Result label
    result_label(inner_result_frame)

    # Displays the result of calculation
    result_box = make_result_box(inner_result_frame)

    # Creates range result box
    range_label = ttk.Label(inner_result_frame, text="Linear Stopping Power:",
                            style="Black.TLabel")
    range_result = tk.Text(inner_result_frame, height=1, borderwidth=3, bd=3,
                           highlightthickness=0, relief='solid')
    range_result.config(bg='white', fg='black', state="disabled", width=entry_width,
                        font=monospace_font)

    if mode == "Mass Stopping Power" and linear:
        # Adds range box
        range_label.pack(pady=(5,1))
        range_result.pack(pady=(1,20))

    # Creates Advanced Settings button
    advanced_button = ttk.Button(root, text="Advanced Settings",
                                 style="Maize.TButton", padding=(0,0),
                                 command=lambda: to_advanced(root, category,
                                                             mode, interactions, common_el,
                                                             common_mat, element, material,
                                                             custom_mat, linear))
    advanced_button.config(width=get_width(["Advanced Settings"]))
    advanced_button.pack(pady=5)

    # Creates Exit button to return to home screen
    exit_button = make_exit_button(root, lambda: exit_to_home(root))

    # Stores nodes into global list
    main_list = [title_frame,
                 mode_frame, empty_frame1,
                 main_frame, empty_frame2,
                 energy_frame, empty_frame3,
                 result_frame, advanced_button, exit_button]

#####################################################################################
# NAVIGATION SECTION
#####################################################################################

"""
This function clears the electron stopping power main screen
in preparation for opening a different screen.
"""
def clear_main():
    global main_list

    # Clears electron stopping power main screen
    for node in main_list:
        node.destroy()
    main_list.clear()

"""
This function transitions from the electron stopping power main screen
to the home screen by first clearing the electron stopping power main screen
and then creating the home screen.
It is called when the Exit button is hit.
"""
def exit_to_home(root):
    root.focus()
    from App.home import return_home
    clear_main()
    return_home(root)

"""
This function transitions from the electron stopping power main screen
to the electron stopping power advanced screen by first clearing the
electron stopping power main screen and then creating the
electron stopping power advanced screen.
It is called when the Advanced Settings button is hit.
"""
def to_advanced(root, category, mode, interactions, common_el,
                common_mat, element, material, custom_mat, linear):
    root.focus()
    from App.Deposition.Electrons.electrons_advanced import electrons_advanced

    clear_main()
    electrons_advanced(root, category, mode, interactions, common_el,
                       common_mat, element, material, custom_mat, linear)