import tkinter as tk
from tkinter import messagebox

from Controllers.table import TableController

class TableView:
    def __init__(self, parent):
        self.parent = parent
        self.controller = TableController()

        self.frame = tk.Frame(parent, bg="white")
        self.frame.pack(fill="both", expand=True)

        self.load_tables()

    def load_tables(self):
        tables = self.controller.load_tables()

        for widget in self.frame.winfo_children():
            widget.destroy()

        if not tables:
            tk.Label(
                self.frame,
                text="Chưa có bàn nào trong hệ thống.",
                bg="white",
                fg="#666",
                font=("Arial", 12),
            ).pack(pady=40)
            return

        for index, table in enumerate(tables):
            table_id = table[0]
            name = table[1]
            status = table[2]

            color = "green" if status == "Trống" else "red"

            btn = tk.Button(
                self.frame,
                text=name,
                bg=color,
                width=15,
                height=3,
                command=lambda id=table_id: self.open_table(id)
            )

            btn.grid(row=index//4, column=index%4, padx=10, pady=10)

    def open_table(self, table_id):
        order = self.controller.open_table(table_id)

        if order:
            messagebox.showinfo("Đặt bàn", f"Mở order hiện tại của bàn {table_id}: {order[0]}")
        else:
            messagebox.showinfo("Đặt bàn", f"Tạo order mới cho bàn {table_id}")
