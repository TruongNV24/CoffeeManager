import tkinter as tk

def create_menu(root, controller, role):
    menu_frame = tk.Frame(root, bg="#34495e", width=200)
    menu_frame.pack(side="left", fill="y")

    def create_button(text, command):
        return tk.Button(
            menu_frame,
            text=text,
            command=command,
            bg="#34495e",
            fg="white",
            font=("Arial", 11),
            bd=0,
            relief="flat",
            activebackground="#1abc9c"
        )

    create_button("🪑 Xem đặt bàn", controller.show_tables).pack(fill="x", ipady=10)
    create_button("☕ Gọi món", controller.show_products).pack(fill="x", ipady=10)

    if role == "Admin":
        create_button("👨‍💼 Nhân viên", controller.show_employees).pack(fill="x", ipady=10)
        create_button("💰 Lương", controller.show_salary).pack(fill="x", ipady=10)
        create_button("🔐 Tài khoản", controller.show_users).pack(fill="x", ipady=10)

    return menu_frame
