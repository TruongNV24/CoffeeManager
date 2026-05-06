import tkinter as tk
from datetime import datetime

from Views.theme import COLORS, FONT_FAMILY, button


class HeaderView:
    def __init__(self, root, username="Admin", role="Staff", on_logout=None):
        self.root = root
        self.username = username
        self.role = role
        self.on_logout = on_logout

        self.frame = tk.Frame(root, bg=COLORS["header"], height=64)
        self.frame.pack(fill="x")
        self.frame.pack_propagate(False)

        self.build_ui()

    def build_ui(self):
        brand = tk.Frame(self.frame, bg=COLORS["header"])
        brand.pack(side="left", padx=18)

        self.app_label = tk.Label(
            brand,
            text="☕ Coffee Manager",
            bg=COLORS["header"],
            fg=COLORS["white"],
            font=(FONT_FAMILY, 18, "bold"),
        )
        self.app_label.pack(anchor="w")

        tk.Label(
            brand,
            text="Quản lý quán cà phê hiện đại",
            bg=COLORS["header"],
            fg="#d8c1a7",
            font=(FONT_FAMILY, 9),
        ).pack(anchor="w")

        self.time_label = tk.Label(
            self.frame,
            bg=COLORS["primary_dark"],
            fg=COLORS["white"],
            padx=14,
            pady=7,
            font=(FONT_FAMILY, 11, "bold"),
        )
        self.time_label.pack(side="left", padx=24)

        self.update_time()

        self.logout_btn = button(
            self.frame,
            text="Đăng xuất",
            variant="danger",
            command=self.logout,
            pady=6,
        )
        self.logout_btn.pack(side="right", padx=(8, 18))

        self.user_label = tk.Label(
            self.frame,
            text=f"👤 {self.username}  •  {self.role}",
            bg=COLORS["header"],
            fg=COLORS["white"],
            font=(FONT_FAMILY, 10, "bold"),
        )
        self.user_label.pack(side="right", padx=10)

    def update_time(self):
        now = datetime.now().strftime("%H:%M:%S")
        self.time_label.config(text=f"🕒 {now}")
        self.root.after(1000, self.update_time)

    def logout(self):
        if self.on_logout:
            self.on_logout()
        else:
            self.root.destroy()
