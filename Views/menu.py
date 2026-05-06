import tkinter as tk

from Views.theme import COLORS, FONT_FAMILY


def create_menu(root, controller, role):
    menu_frame = tk.Frame(root, bg=COLORS["sidebar"], width=230)
    menu_frame.pack(side="left", fill="y")
    menu_frame.pack_propagate(False)

    tk.Label(
        menu_frame,
        text="DASHBOARD",
        bg=COLORS["sidebar"],
        fg="#c9ad91",
        font=(FONT_FAMILY, 9, "bold"),
    ).pack(anchor="w", padx=22, pady=(24, 10))

    def create_button(text, command):
        btn = tk.Button(
            menu_frame,
            text=text,
            command=command,
            bg=COLORS["sidebar"],
            fg=COLORS["white"],
            font=(FONT_FAMILY, 11, "bold"),
            bd=0,
            relief="flat",
            anchor="w",
            padx=22,
            pady=13,
            cursor="hand2",
            activebackground=COLORS["sidebar_hover"],
            activeforeground=COLORS["white"],
        )
        btn.bind("<Enter>", lambda _event: btn.config(bg=COLORS["sidebar_hover"]))
        btn.bind("<Leave>", lambda _event: btn.config(bg=COLORS["sidebar"]))
        return btn

    create_button("🪑  Xem đặt bàn", controller.show_tables).pack(fill="x", pady=2)
    create_button("☕  Gọi món", controller.show_products).pack(fill="x", pady=2)

    if role == "Admin":
        tk.Label(
            menu_frame,
            text="QUẢN TRỊ",
            bg=COLORS["sidebar"],
            fg="#c9ad91",
            font=(FONT_FAMILY, 9, "bold"),
        ).pack(anchor="w", padx=22, pady=(22, 10))
        create_button("👨‍💼  Nhân viên", controller.show_employees).pack(fill="x", pady=2)
        create_button("💰  Lương", controller.show_salary).pack(fill="x", pady=2)
        create_button("🔐  Tài khoản", controller.show_users).pack(fill="x", pady=2)

    tk.Label(
        menu_frame,
        text="Coffee Manager\nMade for everyday operations",
        bg=COLORS["sidebar"],
        fg="#a68a72",
        font=(FONT_FAMILY, 9),
        justify="left",
    ).pack(side="bottom", anchor="w", padx=22, pady=22)

    return menu_frame
