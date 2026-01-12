##### IMPORTS #####
import math
import shelve
import radioactivedecay as rd
from Utility.Functions.gui_utility import no_selection
from Utility.Functions.files import save_file, get_user_data_path
from Core.Decay.Information.energies_dataframe import create_energies_dataframe

#####################################################################################
# EXPORT SECTION
#####################################################################################

"""
This function is called when the Export button is hit.
The function handles the following errors:
   No selected element
   Isotope is stable
   No radiation types selected
   Non-number filter input
   Filter input must be in range [0, 100]
If the error is not applicable, a dataframe is set up
with columns for radiation type, yield, and energy.
The dataframe is populated from the corresponding energies
.json file.
Finally, we pass on the work to the save_file function.
"""
def export_data(root, element, isotope, error_label):
    root.focus()

    # List of neutron irrelevant radiation types
    neutron_irrelevant_types = [
        "Gamma Ray", "Annihilation Photon",
        "X-Ray", "Beta- Particle", "Beta+ Particle",
        "Internal Conversion Electron", "Auger Electron",
        "Alpha Particle"
    ]

    # Gets radiation types and filter percentage from user prefs
    db_path = get_user_data_path("Settings/Decay/Information")
    with shelve.open(db_path) as prefs:
        rad_types = prefs.get("rad_types", [rad_type for rad_type in neutron_irrelevant_types])
        filter_percentage = prefs.get("filter_percentage", "100")

    # Error-check for no selected element
    if element == "":
        error_label.config(style="Error.TLabel", text=no_selection)
        return

    # Error-check for isotope is stable
    if math.isinf(rd.Nuclide(isotope).half_life('s')):
        error_label.config(style="Error.TLabel", text="Error: "+isotope+" is stable.")
        return

    # Error-check for no radiation types selected
    if len(rad_types) == 0:
        error_label.config(style="Error.TLabel", text="Error: No radiation types selected.")
        return

    # Error-check for a non-number filter input
    try:
        filter_percentage = float(filter_percentage)
    except ValueError:
        error_label.config(style="Error.TLabel", text="Error: Non-number filter input.")
        return

    # Error-check for filter input outside of range [0, 100]
    if filter_percentage < 0 or filter_percentage > 100:
        error_label.config(style="Error.TLabel", text="Error: Filter input must be in range [0, 100].")
        return

    error_label.config(style="Error.TLabel", text="")

    # Creates dataframe
    df = create_energies_dataframe(element, isotope, error_label)
    if df is None:
        return

    save_file(df, "Data", error_label, isotope, "energies")