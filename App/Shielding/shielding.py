##### IMPORTS #####
from tkinter import ttk
from App.scroll import scroll_to_top
from App.Shielding.Alphas.alphas_main import alphas_main
from App.Shielding.Photons.photons_main import photons_main
from App.Shielding.Electrons.electrons_main import electrons_main
from Utility.Functions.gui_utility import get_width, make_title_frame

# For global access to nodes on shielding screen
shielding_list = []

#####################################################################################
# MENU SECTION
#####################################################################################

"""
This function creates the shielding screen.
"""
def shielding_menu(root):
    global shielding_list

    title = make_title_frame(root, "Attenuation and Range Data", "Shielding")

    # Creates photons button
    photons_button = ttk.Button(root, text="Photons",
                                command=lambda: to_photons(root),
                                style="Maize.TButton", padding=(0,0))
    photons_button.config(width=get_width(["Photons"]))
    photons_button.pack(pady=5)

    # Creates electrons button
    electrons_button = ttk.Button(root, text="Electrons",
                                  command=lambda: to_electrons(root),
                                  style="Maize.TButton", padding=(0,0))
    electrons_button.config(width=get_width(["Electrons"]))
    electrons_button.pack(pady=5)

    # Creates alphas button
    alphas_button = ttk.Button(root, text="Alphas",
                               command=lambda: to_alphas(root),
                               style="Maize.TButton", padding=(0,0))
    alphas_button.config(width=get_width(["Alphas"]))
    alphas_button.pack(pady=5)

    # Creates Exit button to return to home screen
    exit_button = ttk.Button(root, text="Exit", style="Maize.TButton",
                             padding=(0, 0),
                             command=lambda: exit_to_home(root))
    exit_button.config(width=get_width(["Exit"]))
    exit_button.pack(pady=5)

    # Stores nodes into global list
    shielding_list = [title, photons_button, electrons_button, alphas_button,
                      exit_button]

#####################################################################################
# NAVIGATION SECTION
#####################################################################################

"""
This function clears the shielding screen in preparation
for opening a different screen.
"""
def clear_shielding():
    global shielding_list

    # Clears home
    for node in shielding_list:
        node.destroy()

"""
This function transitions from the shielding screen
to the home screen by first clearing the shielding screen
and then creating the home screen.
It is called when the Exit button is hit.
"""
def exit_to_home(root):
    root.focus()
    from App.home import return_home
    clear_shielding()
    return_home(root)
    scroll_to_top()

"""
This function transitions from the shielding screen
to the photon attenuation main screen by first
clearing the shielding screen and then creating the
photon attenuation main screen.
It is called when the Photons button is hit.
"""
def to_photons(root):
    root.focus()
    clear_shielding()
    photons_main(root)
    scroll_to_top()

"""
This function transitions from the shielding screen
to the electron range main screen by first
clearing the shielding screen and then creating the
electron range main screen.
It is called when the Electrons button is hit.
"""
def to_electrons(root):
    root.focus()
    clear_shielding()
    electrons_main(root)
    scroll_to_top()

"""
This function transitions from the shielding screen
to the alpha range main screen by first
clearing the shielding screen and then creating the
alpha range main screen.
It is called when the Alphas button is hit.
"""
def to_alphas(root):
    root.focus()
    clear_shielding()
    alphas_main(root)
    scroll_to_top()