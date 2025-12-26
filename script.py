##### IMPORTS #####
import os
import sys
from pathlib import Path

# Set working directory
if getattr(sys, "frozen", False):
    base_dir = Path(getattr(sys, "_MEIPASS", "."))
else:
    base_dir = Path(__file__).parent
os.chdir(base_dir)

# Ensures requirements are installed
from Utility.Functions.requirements import check_requirements
check_requirements()

##### IMPORTS #####
import tkinter as tk
from App.home import return_home
from App.style import configure_style
from App.scroll import configure_scrolling
from Utility.Functions.files import set_mpl_cache_dir

# Configure matplotlib
import matplotlib
matplotlib.use('TkAgg')
set_mpl_cache_dir()

##### WINDOW SETUP #####
root = tk.Tk()
root.title("Health Physics Toolbox")
root.geometry("525x750")
root.configure(bg="#F2F2F2")

# Configures style of app
configure_style()

# Configures scrolling
scrollable_frame = configure_scrolling(root)

# Creates home screen upon launch
return_home(scrollable_frame)

# Runs app
root.mainloop()