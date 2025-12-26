#####################################################################################
# REQUIREMENTS SECTION
#####################################################################################

"""
This function ensures the user has all the necessary
requirements installed on their device.
"""
def check_requirements():
    try:
        import matplotlib
        import pandas
        import radioactivedecay
        import PIL
    except ImportError as e:
        import tkinter.messagebox as mb
        mb.showerror(
            "Missing Dependency",
            f"{e}\n\nRun:\n pip install -r requirements.txt"
        )
        raise