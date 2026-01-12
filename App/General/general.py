##### IMPORTS #####
from tkinter import ttk
from App.scroll import scroll_to_top
from App.General.Elements.elements_main import elements_main
from App.General.Isotopes.isotopes_main import isotopes_main
from Utility.Functions.gui_utility import get_width, make_title_frame

# For global access to nodes on general screen
general_list = []

#####################################################################################
# MENU SECTION
#####################################################################################

"""
This function creates the general screen.
"""
def general_menu(root):
    global general_list

    title = make_title_frame(root, "General Information", "General")

    # Creates elements button
    elements_button = ttk.Button(root, text="Elements",
                                 command=lambda: to_elements(root),
                                 style="Maize.TButton", padding=(0, 0))
    elements_button.config(width=get_width(["Elements"]))
    elements_button.pack(pady=5)

    # Creates isotopes button
    isotopes_button = ttk.Button(root, text="Isotopes",
                                 command=lambda: to_isotopes(root),
                                 style="Maize.TButton", padding=(0,0))
    isotopes_button.config(width=get_width(["Isotopes"]))
    isotopes_button.pack(pady=5)

    # Creates Exit button to return to home screen
    exit_button = ttk.Button(root, text="Exit", style="Maize.TButton",
                             padding=(0,0),
                             command=lambda: exit_to_home(root))
    exit_button.config(width=get_width(["Exit"]))
    exit_button.pack(pady=5)

    # Stores nodes into global list
    general_list = [title, elements_button, isotopes_button,
                    exit_button]


#####################################################################################
# NAVIGATION SECTION
#####################################################################################

"""
This function clears the general screen in preparation
for opening a different screen.
"""
def clear_general():
    global general_list

    # Clears home
    for node in general_list:
        node.destroy()

"""
This function transitions from the general screen
to the home screen by first clearing the general screen
and then creating the home screen.
It is called when the Exit button is hit.
"""
def exit_to_home(root):
    root.focus()
    from App.home import return_home
    clear_general()
    return_home(root)
    scroll_to_top()

"""
This function transitions from the general screen
to the elements main screen by first clearing the
general screen and then creating the elements main screen.
It is called when the Elements button is hit.
"""
def to_elements(root):
    root.focus()
    clear_general()
    elements_main(root)
    scroll_to_top()

"""
This function transitions from the general screen
to the isotopes main screen by first clearing the
general screen and then creating the isotopes main screen.
It is called when the Isotopes button is hit.
"""
def to_isotopes(root):
    root.focus()
    clear_general()
    isotopes_main(root)
    scroll_to_top()