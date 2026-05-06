import tkinter as tk

from Views.theme import COLORS, FONT_FAMILY


class ContentView:
    def __init__(self, root):
        self.frame = tk.Frame(root, bg=COLORS["app_bg"])
        self.frame.pack(side="right", expand=True, fill="both")

    def clear(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

    def show_text(self, text, subtitle=None):
        self.clear()
        hero = tk.Frame(self.frame, bg=COLORS["surface"], padx=34, pady=30)
        hero.place(relx=0.5, rely=0.45, anchor="center", width=650, height=280)

        tk.Label(
            hero,
            text="☕",
            bg=COLORS["surface"],
            fg=COLORS["primary"],
            font=(FONT_FAMILY, 56),
        ).pack()
        tk.Label(
            hero,
            text=text,
            bg=COLORS["surface"],
            fg=COLORS["text"],
            font=(FONT_FAMILY, 24, "bold"),
        ).pack(pady=(4, 8))
        tk.Label(
            hero,
            text=subtitle or "Sẵn sàng quản lý bàn, món và nhân sự trong một không gian gọn gàng.",
            bg=COLORS["surface"],
            fg=COLORS["muted"],
            font=(FONT_FAMILY, 12),
            wraplength=540,
            justify="center",
        ).pack()
