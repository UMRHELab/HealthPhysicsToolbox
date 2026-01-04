##### IMPORTS #####
from tkinter import ttk
from App.Dose.ICRP68.icrp68_main import icrp68_main
from Utility.Functions.gui_utility import get_width, make_title_frame

# For global access to nodes on dose screen
dose_list = []

#####################################################################################
# MENU SECTION
#####################################################################################

"""
This function creates the dose screen.
"""
def dose_menu(root):
    global dose_list

    title = make_title_frame(root, "Dose Coefficients", "Dose")

    # Creates ICRP68 button
    icrp68_button = ttk.Button(root, text="ICRP68",
                               command=lambda: to_icrp68(root),
                               style="Maize.TButton", padding=(0,0))
    icrp68_button.config(width=get_width(["ICRP68"]))
    icrp68_button.pack(pady=5)

    # Creates Exit button to return to home screen
    exit_button = ttk.Button(root, text="Exit", style="Maize.TButton",
                             padding=(0, 0),
                             command=lambda: exit_to_home(root))
    exit_button.config(width=get_width(["Exit"]))
    exit_button.pack(pady=5)

    # Stores nodes into global list
    dose_list = [title, icrp68_button,
                 exit_button]

#####################################################################################
# NAVIGATION SECTION
#####################################################################################

"""
This function clears the dose screen in preparation
for opening a different screen.
"""
def clear_dose():
    global dose_list

    # Clears home
    for node in dose_list:
        node.destroy()

"""
This function transitions from the dose screen
to the home screen by first clearing the dose screen
and then creating the home screen.
It is called when the Exit button is hit.
"""
def exit_to_home(root):
    root.focus()
    from App.home import return_home
    clear_dose()
    return_home(root)

"""
This function transitions from the dose screen
to the ICRP68 main screen by first
clearing the dose screen and then creating the
ICRP68 main screen.
It is called when the ICRP68 button is hit.
"""
def to_icrp68(root):
    root.focus()
    clear_dose()
    icrp68_main(root)