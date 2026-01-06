##### IMPORTS #####
import platform
import tkinter as tk
from tkinter import ttk
import tkinter.font as font
from Utility.Functions.logic_utility import valid_saved

#####################################################################################
# ERRORS SECTION
#####################################################################################

### ERROR MESSAGES ###
no_selection = "Error: No selected item."
non_number = "Error: Non-number energy input."
too_low = "Error: Energy too low."
too_high = "Error: Energy too high."
errors = [no_selection, non_number, too_low, too_high]

#####################################################################################
# GUI SECTION
#####################################################################################

"""
This function edits the contents of the result label.
The label needs to be enabled at the start and disabled
at the end in order to prevent the user from being able
to input text.
The previous results are cleared and then the new
results are inserted. If the text being displayed is not
an error, the unit is assed to the end.
"""
def edit_result(result, result_box, num="", den=""):
    # Clears result label and inserts new result
    result_box.config(state="normal")
    result_box.delete("1.0", tk.END)
    result_box.insert(tk.END, result)
    unit = num + "/" + den
    if num == "1":
        unit = den + "\u207B\u00B9"
    if not result in errors and num != "":
        result_box.insert(tk.END, " ")
        result_box.insert(tk.END, unit)
    result_box.config(state="disabled")

"""
This function makes an empty "spacer" frame with y-padding.
This is used to control the space between sections.
"""
def make_spacer(root):
    spacer = tk.Frame(root, bg="#F2F2F2")
    spacer.pack(pady=6)
    return spacer

"""
This function makes a checkbox for an interaction type.
Used for the interaction settings in both the advanced settings
and the export menu.
There is no padding in between checkboxes.
"""
def interaction_checkbox(frame, variable, interaction, command):
    check = ttk.Checkbutton(frame, text=interaction, variable=variable,
                            style="Maize.TCheckbutton", command=command)
    check.pack(anchor="w")
    return check

"""
This function makes a generic Combobox dropdown.
"""
def make_dropdown(frame, var, choices, on_select, **pack_args):
    dropdown = ttk.Combobox(frame, textvariable=var, values=choices,
                            justify="center", style="Maize.TCombobox",
                            state='readonly')
    dropdown.config(width=get_width(choices))
    dropdown.pack(**pack_args)
    dropdown.bind("<<ComboboxSelected>>", on_select)
    return dropdown

"""
This function loads the default value into a Combobox dropdown.
"""
def load_default(dropdown, var, choices):
    def on_map(event):
        if var.get() in choices:
            event.widget.current(choices.index(var.get()))
    dropdown.bind("<Map>", on_map)

"""
This function makes a Combobox dropdown for unit options.
"""
def make_unit_dropdown(frame, var, choices, on_select):
    dropdown = make_dropdown(frame, var, choices, on_select, side='left', padx=5)
    load_default(dropdown, var, choices)
    return dropdown

"""
This function makes a Combobox dropdown for export options.
"""
def make_export_dropdown(frame, var, on_select):
    export_choices = ["Plot", "Data"]
    dropdown = make_dropdown(frame, var, export_choices, on_select)
    load_default(dropdown, var, export_choices)
    return dropdown

"""
This function makes a Combobox dropdown for category options.
"""
def make_category_dropdown(frame, var, select_category, materials=True):
    # Category choices
    if materials:
        choices = ["Common Elements", "All Elements",
                   "Common Materials", "All Materials",
                   "Custom Materials"]
    else:
        choices = ["Common Elements", "All Elements"]

    # Creates dropdown menu for category selection
    _ = make_dropdown(frame, var, choices, select_category)

"""
This function makes an AutocompleteCombobox dropdown for item options.
"""
def make_item_dropdown(root, frame, var, choices, on_enter, on_select=None):
    from App.style import AutocompleteCombobox

    # Logic for when an interacting medium item is selected
    def on_select_default(event):
        event.widget.selection_clear()
        root.focus()

    if not on_select:
        on_select = on_select_default

    # Creates dropdown menu for interacting medium item selection
    item_dropdown = AutocompleteCombobox(frame, textvariable=var, values=choices,
                                         justify="center", style="Maize.TCombobox")
    item_dropdown.set_completion_list(choices)
    item_dropdown.config(width=get_width(choices))
    item_dropdown.pack()
    item_dropdown.bind("<Return>", on_enter)
    item_dropdown.bind("<<ComboboxSelected>>", on_select)
    item_dropdown.bind("<FocusOut>", on_enter)
    return item_dropdown

"""
This function makes a Combobox dropdown for action options.
"""
def make_action_dropdown(frame, var, on_select):
    # Creates dropdown menu for action
    action_choices = ["Add", "Remove"]
    _ = make_dropdown(frame, var, action_choices, on_select)

"""
This function makes a Combobox dropdown for customize category options.
"""
def make_customize_category_dropdown(frame, var, on_select):
    # Creates dropdown menu for customize category
    category_choices = ["Common Elements", "Common Materials", "Custom Materials"]
    _ = make_dropdown(frame, var, category_choices, on_select)

"""
This function is used to make an overall module title.
The titles also have a tooltip for more info.
The title label and tooltip are packed into a frame and returned.
"""
def make_title_frame(root, title, module):
    from App.style import Tooltip

    title_frame = tk.Frame(root, bg="#F2F2F2")
    title_frame.pack()

    title = ttk.Label(title_frame, text=title, style="Blue.TLabel")
    title.pack(side="left", padx=2, pady=(20, 10))

    info_icon = ttk.Label(title_frame, text="\u24D8", style="Blue.TLabel", cursor="hand2")
    info_icon.pack(side="left", padx=2, pady=(20, 10))
    Tooltip(info_icon, module)

    return title_frame

"""
This function makes a basic label and packs it in the provided frame.
"""
def basic_label(frame, text, pady=(0,0)):
    label = ttk.Label(frame, text=text, style="Black.TLabel")
    label.pack(pady=pady)
    return label

"""
This function makes a result label and packs it in the provided frame.
"""
def result_label(frame):
    return basic_label(frame, "Result:", (5,1))

"""
This function makes a result box to display the result
and packs it in the provided frame.
"""
def make_result_box(frame, pady=(1,20)):
    # Creates font for result label and energy entry
    monospace_font = font.Font(family="Menlo", size=12)

    # Output box width
    entry_width = 28 if platform.system() == "Windows" else 32

    # Displays the result of calculation
    result_box = tk.Text(frame, height=1, borderwidth=3, bd=3,
                         highlightthickness=0, relief='solid')
    result_box.config(bg='white', fg='black', state="disabled", width=entry_width,
                      font=monospace_font)
    result_box.pack(pady=pady)

    # Prevent all scrolling
    def block_scroll(*_, **__):
        return "break"

    # Prevent mouse/pad scrolling
    result_box.bind("<MouseWheel>", block_scroll) # Windows & macOS
    result_box.bind("<Button-4>", block_scroll) # Linux scroll up
    result_box.bind("<Button-5>", block_scroll) # Linux scroll down

    # Prevent arrow scrolling
    for key in ("<Up>", "<Down>", "<Left>", "<Right>", "<Prior>", "<Next>"):
        result_box.bind(key, block_scroll)

    # Force view back to top on mouse release to prevent drag-text scrolling
    def reset_view(_):
        result_box.yview_moveto(0) # Always show top line
    result_box.bind("<ButtonRelease-1>", reset_view)

    return result_box

"""
This function creates a generic button.
"""
def make_button(root, text, command):
    button = ttk.Button(root, text=text, style="Maize.TButton",
                        padding=(0,0), command=command)
    button.config(width=get_width([text]))
    button.pack(pady=5)
    return button

"""
This function creates an exit button to return to the home screen.
"""
def make_exit_button(root, command):
    return make_button(root, "Exit", command)

"""
This function creates a back button to return from an advanced settings menu or export menu.
"""
def make_back_button(root, command):
    return make_button(root, "Back", command)

"""
This function creates an advanced settings button to
go to the advanced settings menu.
"""
def make_advanced_button(root, command):
    return make_button(root, "Advanced Settings", command)

"""
This function makes a horizontal frame with a label and an entry.
It is used for both the Enter Material Name and Enter Density sections
in Export menus.
"""
def make_entry_line(frame, text):
    # Creates font
    monospace_font = font.Font(family="Menlo", size=12)

    # Input/output box width
    entry_width = 22 if platform.system() == "Windows" else 32

    # Label
    label = ttk.Label(frame, text=text, style="Black.TLabel")
    label.pack(side="left", padx=(0,5))

    # Entry
    entry = tk.Entry(frame, width=entry_width, insertbackground="black",
                     background="white", foreground="black",
                     borderwidth=3, bd=3, highlightthickness=0, relief='solid',
                     font=monospace_font)
    entry.pack(side="left", padx=(5,0), pady=20)

    return entry

def make_weights_line(frame):
    # Creates font
    monospace_font = font.Font(family="Menlo", size=12)

    # Input/output box width
    entry_width = 16 if platform.system() == "Windows" else 20

    # Frame for element weights example
    ex_frame = tk.Frame(frame, bg="#F2F2F2")
    ex_frame.pack(side="left", padx=(0,30))

    # Element weights label
    basic_label(ex_frame, "Element Weights:")

    # Element weights entry
    entry = tk.Text(frame, width=entry_width, height=10, bg='white', fg='black',
                    insertbackground="black", borderwidth=3, bd=3,
                    highlightthickness=0, relief='solid', font=monospace_font)
    entry.pack(side="left", padx=(30,0), pady=20)

    # Make element weights example
    basic_label(ex_frame, "")
    basic_label(ex_frame, "Example:")
    basic_label(ex_frame, "0.30, Pb")
    basic_label(ex_frame, "0.55, Si")
    basic_label(ex_frame, "0.13, O")
    basic_label(ex_frame, "0.02, K")

    return entry

#####################################################################################
# VERTICAL FRAME SECTION
#####################################################################################

"""
This function creates a vertical frame dependent on the
action and category for Customize Categories settings.
If action is Add and category is Custom Materials,
we create the Add Custom Materials button to direct
to the photon attenuation add custom screen.
Otherwise, we find the choices for the selected
action and category, and create a label, an item dropdown,
and a button to carry out the action.
"""
def make_vertical_frame(root, top_frame, action, category_ar,
                        non_common, common, non_common_m, common_m, custom,
                        button, to_custom):
    from Utility.Functions.customize import carry_action

    # Clear previous button
    button[0].destroy()

    # Make vertical frame
    vertical_frame = tk.Frame(top_frame, bg="#F2F2F2")
    vertical_frame.pack(pady=(5,20))

    if action == "Add" and category_ar == "Custom Materials":
        # Creates Add Custom Materials button
        button[0] = ttk.Button(vertical_frame, text="Add Custom Materials",
                               style="Maize.TButton", padding=(0,0),
                               command=lambda: to_custom())
        button[0].config(width=get_width(["Add Custom Materials"]))
        button[0].pack(pady=(10,0))
        return vertical_frame

    # Stores item
    var = tk.StringVar(root)
    choices = []
    inverse = []
    if action == "Add" and category_ar == "Common Elements":
        var.set(valid_saved("", non_common))
        choices = non_common
        inverse = common
    elif action == "Add" and category_ar == "Common Materials":
        var.set(valid_saved("", non_common_m))
        choices = non_common_m
        inverse = common_m
    elif action == "Remove" and category_ar == "Common Elements":
        var.set(valid_saved("", common))
        choices = common
        inverse = non_common
    elif action == "Remove" and category_ar == "Common Materials":
        var.set(valid_saved("", common_m))
        choices = common_m
        inverse = non_common_m
    elif action == "Remove" and category_ar == "Custom Materials":
        var.set(valid_saved("", custom))
        choices = custom

    # Item label
    basic_label(vertical_frame, "Item:")

    # Logic for when enter is hit when using the item autocomplete combobox
    def on_enter(_):
        value = var.get()
        value = valid_saved(value, choices)
        var.set(value)
        item_dropdown.selection_clear()
        item_dropdown.icursor(tk.END)

    # Creates dropdown menu for interacting medium item selection
    # to be added or removed
    item_dropdown = make_item_dropdown(root, vertical_frame, var, choices, on_enter)

    # Creates button
    button[0] = ttk.Button(vertical_frame, text=action,
                           style="Maize.TButton", padding=(0,0),
                           command=lambda: carry_action(root, action, category_ar,
                                                        choices, inverse, var,
                                                        item_dropdown))
    button[0].config(width=get_width([action]))
    button[0].pack(pady=(10,0))

    return vertical_frame

#####################################################################################
# FONT SECTION
#####################################################################################

"""
This function measures each string in a list in the provided font
and returns the widest string's measurement.
"""
def get_max_string_pixel_width(strings, font_obj):
    return max(font_obj.measure(s) for s in strings) if len(strings) > 0 else 2

"""
This function converts the widest string in a list to a pixel width.
Used for determining dropbox width to fit the longest option.
"""
def get_width(choices):
    # Measures the width of the longest dropdown option in the device's default font
    font_obj = font.nametofont("TkDefaultFont")  # or the font you set in the style
    max_width_px = get_max_string_pixel_width(choices, font_obj)

    # Convert pixels to character width approx
    avg_char_width = font_obj.measure("0")
    char_width = int(max_width_px / avg_char_width) + 2  # +2 for padding/margin

    return char_width