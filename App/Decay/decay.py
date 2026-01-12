##### IMPORTS #####
from tkinter import ttk
from App.scroll import scroll_to_top
from App.Decay.Calculator.decay_calc_main import decay_calc_main
from App.Decay.Information.decay_info_main import decay_info_main
from Utility.Functions.gui_utility import get_width, make_title_frame

# For global access to nodes on decay screen
decay_list = []

#####################################################################################
# MENU SECTION
#####################################################################################

"""
This function creates the decay screen.
"""
def decay_menu(root):
    global decay_list

    title = make_title_frame(root, "Radioactive Decay Data", "Decay")

    # Creates decay information button
    info_button = ttk.Button(root, text="Decay Information",
                             command=lambda: to_info(root),
                             style="Maize.TButton", padding=(0,0))
    info_button.config(width=get_width(["Decay Information"]))
    info_button.pack(pady=5)

    # Creates decay calculator button
    calc_button = ttk.Button(root, text="Decay Calculator",
                             command=lambda: to_calc(root),
                             style="Maize.TButton", padding=(0,0))
    calc_button.config(width=get_width(["Decay Calculator"]))
    calc_button.pack(pady=5)

    # Creates Exit button to return to home screen
    exit_button = ttk.Button(root, text="Exit", style="Maize.TButton",
                             padding=(0,0),
                             command=lambda: exit_to_home(root))
    exit_button.config(width=get_width(["Exit"]))
    exit_button.pack(pady=5)

    # Stores nodes into global list
    decay_list = [title, info_button, calc_button,
                  exit_button]

#####################################################################################
# NAVIGATION SECTION
#####################################################################################

"""
This function clears the decay screen in preparation
for opening a different screen.
"""
def clear_decay():
    global decay_list

    # Clears home
    for node in decay_list:
        node.destroy()

"""
This function transitions from the decay screen
to the home screen by first clearing the decay screen
and then creating the home screen.
It is called when the Exit button is hit.
"""
def exit_to_home(root):
    root.focus()
    from App.home import return_home
    clear_decay()
    return_home(root)
    scroll_to_top()

"""
This function transitions from the decay screen
to the decay information main screen by first
clearing the decay screen and then creating the
decay information main screen.
It is called when the Decay Information button is hit.
"""
def to_info(root):
    root.focus()
    clear_decay()
    decay_info_main(root)
    scroll_to_top()

"""
This function transitions from the decay screen
to the decay calculator main screen by first
clearing the decay screen and then creating the
decay calculator main screen.
It is called when the Decay Calculator button is hit.
"""
def to_calc(root):
    root.focus()
    clear_decay()
    decay_calc_main(root)
    scroll_to_top()