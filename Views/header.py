import tkinter as tk
from datetime import datetime


class HeaderView:
    def __init__(self, root, username="Admin", role="Staff", on_logout=None):
        self.root = root
        self.username = username
        self.role = role
        self.on_logout = on_logout

        self.frame = tk.Frame(root, bg="#2c3e50", height=50)
        self.frame.pack(fill="x")

        self.build_ui()

    def build_ui(self):
        self.app_label = tk.Label(
            self.frame,
            text="☕ Coffee Manager",
            bg="#2c3e50",
            fg="white",
            font=("Arial", 16, "bold"),
        )
        self.app_label.pack(side="left", padx=10)

        self.time_label = tk.Label(
            self.frame,
            bg="#2c3e50",
            fg="white",
            font=("Arial", 10),
        )
        self.time_label.pack(side="left", padx=20)

        self.update_time()

        self.user_label = tk.Label(
            self.frame,
            text=f"👤 {self.username} ({self.role})",
            bg="#2c3e50",
            fg="white",
            font=("Arial", 10),
        )
        self.user_label.pack(side="right", padx=10)

        self.logout_btn = tk.Button(
            self.frame,
            text="Logout",
            bg="#e74c3c",
            fg="white",
            command=self.logout,
        )
        self.logout_btn.pack(side="right", padx=10)

    def update_time(self):
        now = datetime.now().strftime("%H:%M:%S")
        self.time_label.config(text=now)
        self.root.after(1000, self.update_time)

    def logout(self):
        if self.on_logout:
            self.on_logout()
        else:
            self.root.destroy()
