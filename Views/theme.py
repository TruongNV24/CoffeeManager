import tkinter as tk
from tkinter import ttk

# Warm coffee-inspired palette shared by all screens.
COLORS = {
    "app_bg": "#f6efe7",
    "surface": "#fffaf3",
    "surface_alt": "#f1e4d4",
    "sidebar": "#2f1f17",
    "sidebar_hover": "#8b5e34",
    "header": "#3b261c",
    "primary": "#b7793a",
    "primary_dark": "#7a4a24",
    "success": "#2f855a",
    "danger": "#c2410c",
    "warning": "#d97706",
    "info": "#2563eb",
    "text": "#2f241d",
    "muted": "#7c6a5d",
    "border": "#e2c8aa",
    "white": "#ffffff",
}

FONT_FAMILY = "Segoe UI"


def configure_root(root):
    """Apply base window and ttk styles for a softer café dashboard feel."""
    root.configure(bg=COLORS["app_bg"])
    root.option_add("*Font", (FONT_FAMILY, 10))
    root.option_add("*Button.Cursor", "hand2")

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure("TNotebook", background=COLORS["app_bg"], borderwidth=0)
    style.configure(
        "TNotebook.Tab",
        background=COLORS["surface_alt"],
        foreground=COLORS["text"],
        padding=(16, 8),
        font=(FONT_FAMILY, 10, "bold"),
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", COLORS["surface"]), ("active", COLORS["border"])],
        foreground=[("selected", COLORS["primary_dark"])],
    )
    style.configure(
        "Treeview",
        background=COLORS["white"],
        fieldbackground=COLORS["white"],
        foreground=COLORS["text"],
        rowheight=30,
        borderwidth=0,
        font=(FONT_FAMILY, 10),
    )
    style.configure(
        "Treeview.Heading",
        background=COLORS["primary_dark"],
        foreground=COLORS["white"],
        relief="flat",
        padding=(8, 7),
        font=(FONT_FAMILY, 10, "bold"),
    )
    style.map("Treeview", background=[("selected", COLORS["primary"])])
    style.configure("TCombobox", padding=5, fieldbackground=COLORS["white"])


def button(parent, text, command=None, variant="primary", **kwargs):
    palette = {
        "primary": COLORS["primary"],
        "success": COLORS["success"],
        "danger": COLORS["danger"],
        "warning": COLORS["warning"],
        "info": COLORS["info"],
        "ghost": COLORS["surface_alt"],
        "dark": COLORS["sidebar"],
    }
    bg = palette.get(variant, COLORS["primary"])
    fg = COLORS["text"] if variant == "ghost" else COLORS["white"]
    defaults = dict(
        text=text,
        command=command,
        bg=bg,
        fg=fg,
        activebackground=COLORS["primary_dark"] if variant != "ghost" else COLORS["border"],
        activeforeground=COLORS["white"] if variant != "ghost" else COLORS["text"],
        relief="flat",
        bd=0,
        highlightthickness=0,
        padx=14,
        pady=7,
        font=(FONT_FAMILY, 10, "bold"),
        cursor="hand2",
    )
    defaults.update(kwargs)
    return tk.Button(parent, **defaults)


def entry(parent, **kwargs):
    defaults = dict(
        bg=COLORS["white"],
        fg=COLORS["text"],
        insertbackground=COLORS["text"],
        relief="flat",
        highlightthickness=1,
        highlightbackground=COLORS["border"],
        highlightcolor=COLORS["primary"],
        font=(FONT_FAMILY, 10),
    )
    defaults.update(kwargs)
    return tk.Entry(parent, **defaults)


def label(parent, text, **kwargs):
    defaults = dict(
        text=text,
        bg=kwargs.pop("bg", COLORS["surface"]),
        fg=kwargs.pop("fg", COLORS["text"]),
        font=kwargs.pop("font", (FONT_FAMILY, 10)),
    )
    defaults.update(kwargs)
    return tk.Label(parent, **defaults)
