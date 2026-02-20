##### IMPORTS #####
import io
import sys
import csv
import shelve
from Utility.Functions.gui_utility import errors, too_low, too_high
from Utility.Functions.files import resource_path, get_user_data_path
from Utility.Functions.choices import element_choices, material_choices

#####################################################################################
# UNITS SECTION
#####################################################################################

density_numerator = {"mg" : 1000, "g" : 1, "kg" : 0.001}
density_denominator = {"mm\u00B3" : 10 ** 3, "cm\u00B3" : 1,
                       "m\u00B3" : 0.01 ** 3}
atomic_mass_numerator = {"mg" : 1000, "g" : 1, "kg" : 0.001}
atomic_mass_denominator = {"mmol" : 1000, "mol" : 1, "kmol" : 0.001}
energy_units = {"eV" : 0.001 ** 2, "keV" : 0.001,
                "MeV" : 1, "GeV" : 1000}

#####################################################################################
# MATH SECTION
#####################################################################################

"""
This function performs linear interpolation on the provided arguments.
The nearest data are provided (near_low -> val_low) and (near_high -> val_high).
The target is also provided and its value is calculated and returned.
"""
def linear_interpolation(target, near_low, near_high, val_low, val_high):
    difference = near_high - near_low
    percentage = (target - near_low) / difference
    value = val_low + percentage * (val_high - val_low)
    return value

#####################################################################################
# DATA SECTION
#####################################################################################

"""
This function finds the density of the provided item.
If the category is Custom Materials, the density is retrieved
from shelve, where the user-inputted density is stored.
Otherwise, the density is retrieved from the data.
"""
def find_density(category, item):
    if category == "Custom Materials":
        db_path = get_user_data_path('Custom Materials/_' + item)
        with shelve.open(db_path) as db:
            return float(db[item + '_Density'])

    name = 'Elements' if category in element_choices else 'Materials'
    db_path = resource_path('Data/General Data/Density/' + name + '.csv')
    with open(db_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row and row['Name'] == item:
                return float(row['Density'])

    return None

"""
This function handles finding a value from the raw data for the selected item.
Based on the selected category, it passes on the calculation to either
find_data_for_element or find_data_for_material, and then returns the result.
"""
def find_data(category, column, item, energy_target, particle):
    if category in element_choices:
        result = find_data_for_element(item, column, energy_target, particle)
    elif category in material_choices:
        db_path = resource_path('Data/General Data/Material Composition/' + item + '.csv')
        with open(db_path, 'r') as file:
            result = find_data_for_material(file, column, energy_target, particle)
    else:
        db_path = get_user_data_path('Custom Materials/_' + item)
        with shelve.open(db_path) as db:
            stored_data = db[item]
            stored_data = stored_data.replace('\\n', '\n')

        # Create file-like object from the stored string
        csv_file_like = io.StringIO(stored_data)

        result = find_data_for_material(csv_file_like, column,
                                        energy_target, particle)

    return result

"""
This function handles finding a value from the raw data for a material,
by summing the weighted values of each material making up the element.
It uses find_data_for_element to find the coefficient for each element.
"""
def find_data_for_material(file_like, column, energy_target, particle):
    result = 0
    # Parse file
    reader = csv.DictReader(file_like)

    # Sums each component's weighted value
    for row in reader:
        result_of_element = find_data_for_element(row['Element'], column,
                                                  energy_target, particle)
        if result_of_element in errors:
            result = result_of_element
            break
        result_component = float(row['Weight']) * float(result_of_element)
        result += result_component

    return result

"""
This function handles finding a value from the raw data for an element.
The data for the particular element is parsed.
The function handles the following errors:
   Energy too low
   Energy too high
If an exact energy match is found, the coefficient component from
the data is returned directly. Otherwise, if the input did not cause
an error, linear interpolation is used with the closest energy value
on each side of the inputted energy value from the data.
"""
def find_data_for_element(element, column, energy_target, particle):
    # Variables for the nearest energy value on either side
    closest_low = 0.0
    closest_high = float('inf')

    # Variables for the coefficients of the nearest energy values on either side
    low_coefficient = 0.0
    high_coefficient = float('inf')

    # Retrieves name of energy column
    energy_col = "Photon Energy" if particle == "Photons" else\
                 "Kinetic Energy" if particle == "Electrons" else\
                 "Alpha Energy" if particle == "Alphas" else None
    if energy_col is None:
        sys.exit()

    # Opens file
    db_path = resource_path('Data/NIST Coefficients/' + particle + '/Elements/' + element + '.csv')
    with open(db_path, 'r') as file:
        # Reads in file in dictionary format
        reader = csv.DictReader(file)

        for row in reader:
            # Retrieves energy value of row
            energy = float(row[energy_col])

            # Stops searching if we run out of data
            if not row[column]:
                break

            # If energy value matches target exactly, uses
            # the coefficient of this row
            elif energy == energy_target:
                return float(row[column])

            # If energy value is less than the target, uses
            # this energy and its coefficient as the closest
            # value lower than the energy so far, which we know
            # is true because the data is sorted in ascending order
            # by energy
            elif energy < energy_target:
                closest_low = energy
                low_coefficient = float(row[column])

            # If energy value is greater than the target, uses
            # this energy and its coefficient as the closest
            # value higher than the energy and then exits the loop,
            # which we know is true because the data is sorted in
            # ascending order by energy
            else:
                closest_high = energy
                high_coefficient = float(row[column])
                break

    # Error-check for an energy input smaller than all data
    if closest_low == 0.0:
        return too_low

    # Error-check for an energy input larger than all data
    if closest_high == float('inf'):
        return too_high

    # Uses linear interpolation to find the exact coefficient
    return linear_interpolation(energy_target, closest_low, closest_high,
                                low_coefficient, high_coefficient)

"""
This function calculates the range-energy curve value
given a particular energy value.
"""
def range_energy_curve(energy, energy_unit, warning_label):
    if warning_label is not None:
        warning_label.config(text="")

    # Error-check for a negative energy input
    if energy < 0:
        return too_low

    # Warning for model being inaccurate
    if energy < 0.001 or energy > 10 and warning_label is not None:
        # Convert energy back to original unit
        low = 0.001 / energy_units[energy_unit]
        high = 10 / energy_units[energy_unit]

        # Remove float rounding error
        if abs(low - 1000) < 0.001:
            low = 1000.0

        # Scientific notation for large number
        if high > 10000:
            high = f"{high:.0e}"

        warning_label.config(text="Warning: Model is only accurate with input in ["
                                  + str(low).rstrip('0').rstrip('.') + ", "
                                  + str(high).rstrip('0').rstrip('.') + "].")

    # Model
    if energy <= 0.8:
        return 0.407 * pow(energy, 1.38)
    return 0.542 * energy - 0.133

#####################################################################################
# DATAFRAME SECTION
#####################################################################################

"""
This function fills out the dataframe when we are
exporting data for a material. First, we retrieve
the energy values for the dataframe by taking the values
from the raw data of the first element and then removing
any values that are out of range for any of the remaining
elements. Then, for each energy value, we get the data values
for the rest of the row by calling the find_data function.
"""
def make_df_for_material(file_like, df, material, category, mode, energy_unit,
                         submodule, interactions = None):
    # Reads in file
    reader = csv.DictReader(file_like)

    energy_row = "Photon Energy"
    if submodule == "Electrons":
        energy_row = "Kinetic Energy"
    elif submodule == "Alphas":
        energy_row = "Alpha Energy"

    # Create the dataframe
    vals = []
    for row in reader:
        db_path = resource_path(f'Data/NIST Coefficients/{submodule}/Elements/{row['Element']}.csv')
        if len(vals) == 0:
            with open(db_path, 'r') as file:
                # Reads in file
                reader2 = csv.DictReader(file)

                # Gets energy values to use as dots
                for row2 in reader2:
                    if not interactions and submodule == "Photons":
                        try:
                            _ = float(row2[mode])
                            vals.append(float(row2[energy_row]))
                        except ValueError:
                            pass
                    else:
                        vals.append(float(row2[energy_row]))
        else:
            with open(db_path, 'r') as file:
                # Reads in file
                reader2 = csv.DictReader(file)

                new_vals = []
                # Gets energy values to use as dots
                for row2 in reader2:
                    if not interactions and submodule == "Photons":
                        try:
                            _ = float(row2[mode])
                            new_vals.append(float(row2[energy_row]))
                        except ValueError:
                            pass
                    else:
                        new_vals.append(float(row2[energy_row]))
                max_val = max(new_vals)
                min_val = min(new_vals)
                vals = [val for val in vals if min_val <= val <= max_val]

    # Gets rid of bad R.E.C. energy values
    if mode == "Range-Energy Curve":
        min_val = 0.001
        max_val = 10
        vals = [val for val in vals if min_val <= val <= max_val]

    # Finds the data at each energy value and adds to dataframe
    for index, val in enumerate(vals):
        row = [val]
        if interactions:
            for interaction in interactions:
                x = find_data(category, interaction, material, val, submodule)
                row.append(x)
        else:
            if mode == "Range-Energy Curve":
                x = range_energy_curve(val, energy_unit, None)
            else:
                x = find_data(category, mode, material, val, submodule)
            row.append(x)
        df.loc[index] = row