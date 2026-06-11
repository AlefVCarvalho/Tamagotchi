import os
import sys
import tkinter as tk


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def load_photo(relative_path):
    path = resource_path(relative_path)
    if not os.path.exists(path):
        return None
    try:
        return tk.PhotoImage(file=path)
    except tk.TclError:
        return None
