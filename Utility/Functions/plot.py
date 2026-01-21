##### IMPORTS #####
import matplotlib.pyplot as plt

#####################################################################################
# PLOT SECTION
#####################################################################################

"""
This function configures the plot that is being exported
using the dataframe and other information.
First, the plot is cleared from any previous exports.
Then, the dataframe is plotted accordingly.
The title, legend, and axis titles are all configured
and the axis scales are set to logarithmic.
"""
def configure_plot(interactions, df, energy_col, mode_col, title):
    # Clear from past plots
    plt.clf()

    # Plot the data
    if interactions:
        for interaction in interactions:
            plt.plot(df[energy_col], df[interaction], marker='o', label=interaction)
    else:
        plt.plot(df[energy_col], df[mode_col], marker='o', label=mode_col)

    # Configure plot
    plt.title(title, fontsize=8.5)
    plt.xscale('log')
    plt.yscale('log')
    if interactions:
        plt.legend()
    plt.xlabel(energy_col)
    plt.ylabel(mode_col)
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()