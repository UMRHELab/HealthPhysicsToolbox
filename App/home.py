##### IMPORTS #####
from tkinter import ttk
from App.Dose.dose import dose_menu
from App.Decay.decay import decay_menu
from App.General.general import general_menu
from App.Shielding.shielding import shielding_menu
from App.Deposition.deposition import deposition_menu
from Utility.Functions.gui_utility import get_width, make_title_frame

# For global access to nodes on home screen
home_list = []

#####################################################################################
# MENU SECTION
#####################################################################################

"""
This function creates the home screen.
"""
def return_home(root):
    global home_list

    title = make_title_frame(root, "Health Physics Toolbox", "Home")

    # Creates button for shielding menu
    shielding_button = ttk.Button(root, text="Attenuation and Range Data",
                                  command=lambda: shielding(root),
                                  style="Maize.TButton", padding=(0,0))
    shielding_button.config(width=get_width(["Attenuation and Range Data"]))
    shielding_button.pack(pady=5)

    # Creates button for deposition menu
    deposition_button = ttk.Button(root, text="Energy Deposition Data",
                                   command=lambda: deposition(root),
                                   style="Maize.TButton", padding=(0,0))
    deposition_button.config(width=get_width(["Energy Deposition Data"]))
    deposition_button.pack(pady=5)

    # Creates button for decay menu
    decay_button = ttk.Button(root, text="Radioactive Decay Data",
                              command=lambda: decay(root),
                              style="Maize.TButton", padding=(0,0))
    decay_button.config(width=get_width(["Radioactive Decay Data"]))
    decay_button.pack(pady=5)

    # Creates button for dose menu
    dose_button = ttk.Button(root, text="Dose Coefficients",
                             command=lambda: dose(root),
                             style="Maize.TButton", padding=(0,0))
    dose_button.config(width=get_width(["Dose Coefficients"]))
    dose_button.pack(pady=5)

    # Creates button for general info menu
    general_button = ttk.Button(root, text="General Information",
                                command=lambda: general(root),
                                style="Maize.TButton", padding=(0,0))
    general_button.config(width=get_width(["General Information"]))
    general_button.pack(pady=5)

    # Stores nodes into global list
    home_list = [title, shielding_button, deposition_button, decay_button,
                 dose_button, general_button]

#####################################################################################
# NAVIGATION SECTION
#####################################################################################

"""
This function clears the home screen in preparation
for opening a different screen.
"""
def clear_home():
    global home_list

    # Clears home
    for node in home_list:
        node.destroy()

"""
This function transitions from the home screen
to the shielding screen by first clearing the
home screen and then creating the shielding screen.
It is called when the Attenuation and Range Data button is hit.
"""
def shielding(root):
    root.focus()
    clear_home()
    shielding_menu(root)

"""
This function transitions from the home screen
to the deposition screen by first clearing the
home screen and then creating the deposition screen.
It is called when the Energy Deposition Data button is hit.
"""
def deposition(root):
    root.focus()
    clear_home()
    deposition_menu(root)

"""
This function transitions from the home screen
to the decay screen by first clearing the
home screen and then creating the decay screen.
It is called when the Radioactive Decay Data button is hit.
"""
def decay(root):
    root.focus()
    clear_home()
    decay_menu(root)

"""
This function transitions from the home screen
to the dose screen by first clearing the
home screen and then creating the dose screen.
It is called when the Dose Coefficients button is hit.
"""
def dose(root):
    root.focus()
    clear_home()
    dose_menu(root)

"""
This function transitions from the home screen
to the general screen by first clearing the
home screen and then creating the general screen.
It is called when the General Information button is hit.
"""
def general(root):
    root.focus()
    clear_home()
    general_menu(root)