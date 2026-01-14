##### IMPORTS #####
import tkinter as tk
from tkinter import ttk

# Global variables indicating the visibility of the scrollbars
scrollbar_y_visible = True
scrollbar_x_visible = True

# Global variable for canvas
canvas : tk.Canvas

#####################################################################################
# MAIN SECTION
#####################################################################################

"""
This function calls the single-purpose functions
to complete all of the scrolling configurations.
It is called by script.py.
The scrollable frame is returned to be filled with
the contents of the app.
"""
def configure_scrolling(root):
    global canvas
    container = make_container(root)
    left_frame = make_left_frame(container)
    right_frame = make_right_frame(container)
    make_canvas(left_frame)
    scrollbar_y, scrollbar_x = make_scrollbars(left_frame, right_frame)
    scrollable_frame, canvas_window = make_scrollable_frame()
    make_scroll_update(scrollable_frame, canvas_window, scrollbar_y, scrollbar_x)
    make_mouse_scroll()
    make_key_scroll(root)
    return scrollable_frame

#####################################################################################
# GUI SECTION
#####################################################################################

"""
This function makes the main container frame
for the app.
"""
def make_container(root):
    # Wraps whole app in a container for vertical alignment
    container = tk.Frame(root, bg="#F2F2F2")
    container.pack(fill="both", expand=True)
    return container

"""
This function makes the left frame for the app.
This is the region with the x-scrollbar.
"""
def make_left_frame(container):
    # Creates canvas
    left_frame = tk.Canvas(container, bg="#F2F2F2", highlightthickness=0, bd=0)
    left_frame.pack(side="left", fill="both", expand=True)
    return left_frame

"""
This function makes the right frame for the app.
This is the region with the y-scrollbar.
"""
def make_right_frame(container):
    # Creates canvas
    right_frame = tk.Frame(container, bg="#F2F2F2", highlightthickness=0, bd=0)
    right_frame.pack(side="right", fill="y")
    return right_frame

"""
This function makes the canvas for the app.
This is the region excluding both scrollbars.
"""
def make_canvas(left_frame):
    global canvas
    # Creates canvas
    canvas = tk.Canvas(left_frame, bg="#F2F2F2", highlightthickness=0, bd=0)
    canvas.pack(side="top", fill="both", expand=True)

"""
This function makes both scrollbars for the app.
The x-scrollbar is placed at the bottom of the left frame.
The y-scrollbar is placed in the right frame.
"""
def make_scrollbars(left_frame, right_frame):
    global canvas
    # Creates scrollbars
    scrollbar_y = ttk.Scrollbar(right_frame, orient="vertical", command=canvas.yview)
    scrollbar_y.pack(side="top", fill="y")
    scrollbar_x = ttk.Scrollbar(left_frame, orient="horizontal", command=canvas.xview)
    scrollbar_x.pack(side="bottom", fill="x")
    canvas.configure(xscrollcommand=scrollbar_x.set, yscrollcommand=scrollbar_y.set)
    return scrollbar_y, scrollbar_x

"""
This function makes the scrollable frame for the app.
This is placed inside of the canvas.
"""
def make_scrollable_frame():
    global canvas
    # Creates a frame inside the canvas
    scrollable_frame = tk.Frame(canvas, bg="#F2F2F2")
    canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    return scrollable_frame, canvas_window

#####################################################################################
# SCROLLING SECTION
#####################################################################################

"""
This function creates the logic to update the scrollbars' visibility.
Whenever the window size is updated, the inner function
update_scroll_visibility is ran to check whether each scrollbar
is needed.
"""
def make_scroll_update(scrollable_frame, canvas_window, scrollbar_y, scrollbar_x):
    global canvas
    # Logic to show/hide scrollbar
    def update_scroll_visibility(event):
        global scrollbar_y_visible, scrollbar_x_visible
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.update_idletasks()
        needs_scrollbar_y = scrollable_frame.winfo_reqheight() > canvas.winfo_height()
        needs_scrollbar_x = scrollable_frame.winfo_reqwidth() > canvas.winfo_width()

        if not needs_scrollbar_x:
            canvas.itemconfig(canvas_window, width=event.width if event else 525)

        if needs_scrollbar_y and not scrollbar_y_visible:
            scrollbar_y.pack(side="right", fill="y")
            scrollbar_y_visible = True
        elif not needs_scrollbar_y and scrollbar_y_visible:
            scrollbar_y.pack_forget()
            scrollbar_y_visible = False

        if needs_scrollbar_x and not scrollbar_x_visible:
            scrollbar_x.pack(side="bottom", fill="x")
            scrollbar_x_visible = True
        elif not needs_scrollbar_x and scrollbar_x_visible:
            scrollbar_x.pack_forget()
            scrollbar_x_visible = False

    # Bind size changes
    scrollable_frame.bind("<Configure>", update_scroll_visibility)
    canvas.bind("<Configure>", update_scroll_visibility)
    update_scroll_visibility(None)

"""
This function configures mouse/pad scrolling to scroll the app.
"""
def make_mouse_scroll():
    global canvas
    # Makes Canvas scrollable with mouse/pad
    def _on_mousewheel(event):
        if scrollbar_y_visible:
            canvas.yview_scroll(-1 * int(event.delta), "units")
        if scrollbar_x_visible:
            canvas.xview_scroll(-1 * int(event.delta), "units")

    canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
    canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

    # Linux bindings
    canvas.bind("<Button-4>", _on_mousewheel)
    canvas.bind("<Button-5>", _on_mousewheel)

"""
This function configures arrow keys to scroll the app.
"""
def make_key_scroll(root):
    global canvas
    # Makes Canvas scrollable with up/down keys
    def on_up(_):
        if scrollbar_y_visible:
            canvas.yview_scroll(-1, "units")

    def on_down(_):
        if scrollbar_y_visible:
            canvas.yview_scroll(1, "units")

    def on_left(_):
        if scrollbar_x_visible:
            canvas.xview_scroll(-1, "units")

    def on_right(_):
        if scrollbar_x_visible:
            canvas.xview_scroll(1, "units")

    root.bind_all("<KeyPress-Up>", on_up)
    root.bind_all("<KeyPress-Down>", on_down)
    root.bind_all("<KeyPress-Left>", on_left)
    root.bind_all("<KeyPress-Right>", on_right)

def scroll_to_top():
    canvas.yview_moveto(0)