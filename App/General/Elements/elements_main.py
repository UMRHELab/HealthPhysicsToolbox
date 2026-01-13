##### IMPORTS #####
import tkinter as tk
from tkinter import ttk
from App.style import SectionFrame
from App.scroll import scroll_to_top
from Utility.Functions.choices import get_choices
from Core.General.Elements.elements import handle_action
from Utility.Functions.logic_utility import get_item, valid_saved
from Utility.Functions.gui_utility import (
    get_width,
    basic_label,
    make_title_frame,
    make_category_dropdown, make_item_dropdown,
    make_exit_button, make_advanced_button, make_display_button, make_export_button
)

# For global access to nodes on elements main screen
main_list = []

#####################################################################################
# MENU SECTION
#####################################################################################

"""
This function sets up the general element main screen.
The following sections and widgets are created:
   Module Title (Element Information)
   Select Element section
   Result section (title dependent on Calculation Mode)
   Advanced Settings button
   Exit button
This function contains all of the logic involving these widgets'
behaviors.
The sections and widgets are stored in main_list so they can be
accessed later by clear_main.
"""
def elements_main(root, category="Common Elements", common_el="Ag", element="Ac"):
    global main_list

    # Makes title frame
    title_frame = make_title_frame(root, "Element Information", "General/Elements")

    # Gets the element options
    choices = get_choices(category, "General", "")

    # Gets common elements
    common_elements = get_choices("Common Elements", "General", "")

    # Make sure common element is a valid selection
    common_el = valid_saved(common_el, common_elements)

    # Frame for element selection
    main_element_frame = SectionFrame(root, title="Select Element")
    main_element_frame.pack()
    inner_element_frame = main_element_frame.get_inner_frame()

    # Stores category selection and sets default
    var_category = tk.StringVar(root)
    var_category.set(category)

    # Logic for when an element category is selected
    def select_category(event):
        nonlocal choices, category, common_el, element

        event.widget.selection_clear()
        category = var_category.get()

        # Updates element dropdown to match category
        choices = get_choices(category, "General", "")
        var_element.set(get_item(category, common_el, "", element, "", ""))
        element_dropdown.set_completion_list(choices)
        element_dropdown.config(values=choices, width=get_width(choices))
        root.focus()

    # Frame for element category selection
    category_frame = tk.Frame(inner_element_frame, bg="#F2F2F2")
    category_frame.pack(pady=(15,5))

    # Category label
    basic_label(category_frame, "Category:")

    # Creates dropdown menu for category selection
    make_category_dropdown(category_frame, var_category, select_category, False)

    # Logic for when enter is hit when using the element autocomplete combobox
    def on_enter(_):
        nonlocal common_el, element
        value = var_element.get()

        if value not in choices:
            # Falls back on default if invalid element is typed in
            var_element.set(get_item(category, common_el, "", element, "", ""))
        else:
            # Stores most recent items
            if category == "All Elements":
                element = value
            else:
                common_el = value

        element_dropdown.selection_clear()
        element_dropdown.icursor(tk.END)

    # Frame for element selection
    element_frame = tk.Frame(inner_element_frame, bg="#F2F2F2")
    element_frame.pack(pady=(5,20))

    # Element label
    basic_label(element_frame, "Element:")

    # Stores element selection and sets default
    var_element = tk.StringVar(root)
    var_element.set(get_item(category, common_el, "", element, "", ""))

    # Creates dropdown menu for element
    element_dropdown = make_item_dropdown(root, element_frame, var_element, choices, on_enter)

    # Creates warning label for bad input
    error_label = ttk.Label(root, text="", style="Error.TLabel")
    error_label.pack(pady=5)

    # Frame for Display & Export buttons
    action_frame = tk.Frame(root, bg="#F2F2F2")
    action_frame.pack(pady=5)

    # Creates Display button
    make_display_button(action_frame, lambda: handle_action(root, var_element.get(), error_label, False))

    # Creates Export button
    make_export_button(action_frame, lambda: handle_action(root, var_element.get(), error_label, True))

    # Creates Advanced Settings button
    advanced_button = make_advanced_button(root, lambda: to_advanced(root, category,
                                                                     common_el, element))

    # Creates Exit button to return to home screen
    exit_button = make_exit_button(root, lambda: exit_to_home(root))

    # Stores nodes into global list
    main_list = [title_frame, main_element_frame,
                 action_frame,
                 error_label, advanced_button, exit_button]

#####################################################################################
# NAVIGATION SECTION
#####################################################################################

"""
This function clears the elements main screen
in preparation for opening a different screen.
"""
def clear_main():
    global main_list

    # Clears elements main screen
    for node in main_list:
        node.destroy()
    main_list.clear()

"""
This function transitions from the elements main screen
to the home screen by first clearing the elements main screen
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
This function transitions from the elements main screen
to the elements advanced screen by first clearing the
elements main screen and then creating the
elements advanced screen.
It is called when the Advanced Settings button is hit.
"""
def to_advanced(root, category, common_el, element):
    root.focus()
    from App.General.Elements.elements_advanced import elements_advanced

    clear_main()
    elements_advanced(root, category, common_el, element)
    scroll_to_top()