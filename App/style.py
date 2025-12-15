##### IMPORTS #####
import platform
import tkinter as tk
from tkinter import ttk
import tkinter.font as font
from Utility.Functions.files import resource_path
from Utility.Functions.choices import get_choices
from Utility.Functions.gui_utility import get_max_string_pixel_width

#####################################################################################
# COLORS SECTION
#####################################################################################

"""
This function configures all of the colors and fonts
for the app's widgets.
"""
def configure_style():
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Maize.TButton",
                    background="#FFCB05",
                    foreground="black")
    style.configure("Maize.TCombobox",
                    background="#FFCB05",
                    foreground="black")
    style.map("Maize.TCombobox",
              fieldbackground=[('readonly', "white"), ('!readonly', "white")])
    style.map("Maize.TCombobox",
              background=[('readonly', "#FFCB05"), ('!readonly', "#FFCB05")])
    style.map("Maize.TCombobox",
              foreground=[('readonly', "black"), ('!readonly', "black")])
    style.configure("Maize.TCheckbutton",
                    background="#F2F2F2",
                    foreground="#00274C",
                    font=("TkDefaultFont", 9 if platform.system() == "Windows" else 13,
                          "bold"))
    style.map("Maize.TCheckbutton",
              background=[('active', "#F2F2F2")])
    style.map(
        "Maize.TCheckbutton",
        indicatorbackground=[
            ("alternate", "white"),
            ("!selected", "white"),
            ("selected", "white"),
        ],
        indicatorforeground=[
            ("alternate", "black"),
        ]
    )
    style.configure("White.TLabel",
                    background="#00274C",
                    foreground="white",
                    font=("Verdana", 13 if platform.system() == "Windows" else 16))
    style.configure("Black.TLabel",
                    background="#F2F2F2",
                    foreground="black",
                    font=("TkDefaultFont", 9 if platform.system() == "Windows" else 13,
                          "bold"))
    style.configure("Error.TLabel",
                    background="#F2F2F2",
                    foreground="red",
                    font=("TkDefaultFont", 8 if platform.system() == "Windows" else 12,
                          "bold"))
    style.configure("Success.TLabel",
                    background="#F2F2F2",
                    foreground="black",
                    font=("TkDefaultFont", 8 if platform.system() == "Windows" else 12,
                          "bold"))
    style.configure("Blue.TLabel",
                    background="#F2F2F2",
                    foreground="#00274C",
                    font=("Verdana", 17 if platform.system() == "Windows" else 20, "bold"))

#####################################################################################
# SECTION BORDERS SECTION
#####################################################################################

"""
This class represents a full section with a border, title bar, title,
and inside frame for the section's contents.
"""
class SectionFrame(tk.Frame):
    def __init__(self, parent, title="", *args, **kwargs):
        # Transparent-style frame (inherits parent's bg)
        bg_color = "#F2F2F2"
        super().__init__(parent, bg=bg_color, *args, **kwargs)

        # Border frame to simulate an outline
        self.border_frame = tk.Frame(self, bg="#00274C")
        self.border_frame.pack(padx=1, pady=10)

        # Sets the height of the title bar
        tk_font = font.Font(family="Verdana",
                            size=13 if platform.system() == "Windows" else 16)
        font_height = tk_font.metrics("linespace")
        title_height = max(24, font_height + 5)

        # Inner frame (blends with background)
        self.inner_frame = tk.Frame(self.border_frame, bg=bg_color)
        self.inner_frame.pack(padx=4, pady=(title_height, 4))

        # Empty frame to set a consistent width for each section
        custom = get_choices("Custom Materials", "", "Photons")
        mats = get_choices("All Materials", "Shielding", "Photons")
        custom_width = (get_max_string_pixel_width(custom,
                                                   font.nametofont("TkDefaultFont")) // 2 + 20) * 2
        mats_width = (get_max_string_pixel_width(mats,
                                                 font.nametofont("TkDefaultFont")) // 2 + 20) * 2
        width = max(400, custom_width, mats_width)

        if platform.system() == 'Windows':
            width += 60

        width_frame = tk.Frame(self.inner_frame, bg="#F2F2F2", width=width)
        width_frame.pack()
        width_frame.pack_propagate(False)

        # Title bar
        self.title_bar = tk.Frame(self.border_frame, bg="#00274C", height=title_height)
        self.title_bar.place(x=0, y=0, relwidth=1)

        self.title_label = ttk.Label(
            self.title_bar, text=title, style="White.TLabel"
        )
        self.title_label.pack()
        self.title_label.place(relx=0.5, rely=0.5, anchor="center")

    def get_inner_frame(self):
        return self.inner_frame

    def change_title(self, title):
        self.title_label.destroy()
        self.title_label = ttk.Label(
            self.title_bar, text=title, style="White.TLabel"
        )
        self.title_label.pack()
        self.title_label.place(relx=0.5, rely=0.5, anchor="center")

#####################################################################################
# TOOLTIP SECTION
#####################################################################################

"""
This class represents a tooltip for more information on
a particular module.
"""
class Tooltip:
    def __init__(self, widget, module):
        self.widget = widget
        self.module = module
        self.tooltip_window = None
        self.after_id = None
        self.delay = 10
        widget.bind("<Enter>", self.schedule_tooltip)
        widget.bind("<Leave>", self.cancel_tooltip)

    def schedule_tooltip(self, _):
        self.after_id = self.widget.after(self.delay, self.show_tooltip)

    def cancel_tooltip(self, _):
        if self.after_id:
            self.widget.after_cancel(self.after_id)
            self.after_id = None
        self.hide_tooltip()

    def show_tooltip(self):
        if self.tooltip_window or not self.module:
            return
        x = self.widget.winfo_rootx() + (52 if platform.system() == "Windows" else 26)
        y = self.widget.winfo_rooty() + (24 if platform.system() == "Windows" else 12)
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        db_path = resource_path('Utility/Modules/' + self.module + '/Info.txt')
        with open(db_path, 'r') as file:
            text = file.read()
        label = ttk.Label(
            tw, text=text, justify='left', style="Blue.TLabel",
            relief='solid', borderwidth=1,
            font=("Verdana", 12, "normal")
        )
        label.pack(ipadx=1)

    def hide_tooltip(self):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

#####################################################################################
# AUTOCOMPLETE COMBOBOX SECTION
#####################################################################################

"""
Subclass of Tkinter.Combobox that features autocompletion.
To enable autocompletion use set_completion_list(list) to define
a list of possible strings to hit.
"""
class AutocompleteCombobox(ttk.Combobox):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self._completion_list = []
        self._hits = []
        self._hit_index = 0
        self.position = 0

    def set_completion_list(self, completion_list):
        """Use our completion list as our dropdown selection menu, arrows move through menu."""
        self._completion_list = sorted(completion_list, key=lambda s: s.lower())  # Work with a sorted list
        self._hits = []
        self._hit_index = 0
        self.position = 0
        self.bind('<KeyRelease>', self.handle_keyrelease)
        self['values'] = self._completion_list  # Setup our popup menu

    def autocomplete(self, delta=0):
        """autocomplete the Combobox, delta may be 0/1/-1 to cycle through possible hits"""
        if delta:  # need to delete selection otherwise we would fix the current position
            self.delete(self.position, tk.END)
        else:  # set position to end so selection starts where text entry ended
            self.position = len(self.get())
        # collect hits
        _hits = []
        for item in self._completion_list:
            if item.lower().startswith(self.get().lower()):  # Match case insensitively
                _hits.append(item)
        # if we have a new hit list, keep this in mind
        if _hits != self._hits:
            self._hit_index = 0
            self._hits = _hits
        # only allow cycling if we are in a known hit list
        if _hits == self._hits and self._hits:
            self._hit_index = (self._hit_index + delta) % len(self._hits)
        # now finally perform the autocompletion
        if self._hits:
            self.delete(0, tk.END)
            self.insert(0, self._hits[self._hit_index])
            self.select_range(self.position, tk.END)

    def handle_keyrelease(self, event):
        """event handler for the keyrelease event on this widget"""
        if event.keysym == "BackSpace":
            self.delete(self.index(tk.INSERT), tk.END)
            self.position = self.index(tk.END)
        if event.keysym == "Left":
            if self.position < self.index(tk.END):  # delete the selection
                self.delete(self.position, tk.END)
            else:
                self.position = self.position - 1  # delete one character
                self.delete(self.position, tk.END)
        if event.keysym == "Right":
            self.position = self.index(tk.END)  # go to end (no selection)
        if len(event.keysym) == 1:
            self.autocomplete()
        # No need for up/down, we'll jump to the popup
        # list at the position of the autocompletion