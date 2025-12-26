#####################################################################################
# LOGIC SECTION
#####################################################################################

"""
This function returns the list of selected interactions
given the list of all interactions and the list of the
variables storing whether each interaction is selected.
"""
def get_interactions(interaction_choices, interaction_vars):
    return [interaction_choices[x] for x in range(len(interaction_choices))
            if interaction_vars[x].get() == 1]

"""
This function defaults a saved item choice to the first in the list
of options in case it was removed from the category. If the list of
options is empty, it defaults to an empty string.
"""
def valid_saved(saved, choices):
    return saved if saved in choices else choices[0] if len(choices) > 0 else ""

"""
This function returns the correct saved item based on the selected category.
"""
def get_item(category, common_el, common_mat, element, material, custom_mat):
    return common_el if category == "Common Elements" else\
           common_mat if category == "Common Materials" else\
           element if category == "All Elements" else\
           material if category == "All Materials" else\
           custom_mat if category == "Custom Materials" else ""

"""
This function returns the relevant item based on the
calculation mode.
It is used in two cases:
1. To retrieve the correct unit out of the saved units
   of each mode
2. To retrieve the correct list of unit choices for the
   selected mode
"""
def get_unit(units, modes, mode):
    return dict(zip(modes, units))[mode]