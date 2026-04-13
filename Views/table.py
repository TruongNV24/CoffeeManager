import tkinter as tk
from tkinter import messagebox

from Controllers.table import TableController


class TableView:
    def __init__(self, parent):
        self.parent = parent
        self.controller = TableController()
        self.selected_table_id = None

        self.frame = tk.Frame(parent, bg="white")
        self.frame.pack(fill="both", expand=True)

        self.build_crud_panel()
        self.load_tables()

    def build_crud_panel(self):
        form_frame = tk.Frame(self.frame, bg="white")
        form_frame.pack(fill="x", padx=20, pady=15)

        tk.Label(form_frame, text="Tên bàn:", bg="white", font=("Arial", 11)).grid(
            row=0, column=0, sticky="w", padx=(0, 8)
        )
        self.name_entry = tk.Entry(form_frame, width=24, font=("Arial", 11))
        self.name_entry.grid(row=0, column=1, sticky="w")

        tk.Label(form_frame, text="Trạng thái:", bg="white", font=("Arial", 11)).grid(
            row=0, column=2, sticky="w", padx=(18, 8)
        )
        self.status_var = tk.StringVar(value="Trống")
        status_options = ("Trống", "Đang dùng")
        self.status_menu = tk.OptionMenu(form_frame, self.status_var, *status_options)
        self.status_menu.config(width=10)
        self.status_menu.grid(row=0, column=3, sticky="w")

        action_frame = tk.Frame(form_frame, bg="white")
        action_frame.grid(row=0, column=4, padx=(24, 0))

        tk.Button(
            action_frame, text="Thêm", bg="#2ecc71", fg="white", command=self.add_table
        ).pack(side="left", padx=4)
        tk.Button(
            action_frame,
            text="Cập nhật",
            bg="#3498db",
            fg="white",
            command=self.update_table,
        ).pack(side="left", padx=4)
        tk.Button(
            action_frame, text="Xóa", bg="#e74c3c", fg="white", command=self.delete_table
        ).pack(side="left", padx=4)
        tk.Button(action_frame, text="Làm mới", command=self.reset_form).pack(
            side="left", padx=4
        )

        self.list_frame = tk.Frame(self.frame, bg="white")
        self.list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def load_tables(self):
        tables = self.controller.load_tables()

        for widget in self.list_frame.winfo_children():
            widget.destroy()

        if not tables:
            tk.Label(
                self.list_frame,
                text="Chưa có bàn nào trong hệ thống.",
                bg="white",
                fg="#666",
                font=("Arial", 12),
            ).pack(pady=40)
            return

        tk.Label(
            self.list_frame,
            text="Danh sách bàn (nhấn để chọn):",
            bg="white",
            font=("Arial", 12, "bold"),
        ).pack(anchor="w", pady=(5, 12))

        grid_frame = tk.Frame(self.list_frame, bg="white")
        grid_frame.pack(fill="both", expand=True)

        for index, table in enumerate(tables):
            table_id = table[0]
            name = table[1]
            status = table[2]

            color = "green" if status == "Trống" else "red"

            btn = tk.Button(
                grid_frame,
                text=f"{name}\n({status})",
                bg=color,
                width=15,
                height=3,
                command=lambda data=table: self.select_table(data),
            )

            btn.grid(row=index // 4, column=index % 4, padx=10, pady=10)

    def select_table(self, table):
        table_id, name, status = table
        self.selected_table_id = table_id
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, name or "")
        self.status_var.set(status or "Trống")

    def open_table(self, table_id):
        order = self.controller.open_table(table_id)

        if order:
            messagebox.showinfo("Đặt bàn", f"Mở order hiện tại của bàn {table_id}: {order[0]}")
        else:
            messagebox.showinfo("Đặt bàn", f"Tạo order mới cho bàn {table_id}")

    def add_table(self):
        name = self.name_entry.get().strip()
        status = self.status_var.get()

        if not name:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập tên bàn.")
            return

        self.controller.add_table(name, status)
        self.load_tables()
        self.reset_form(show_message=False)

    def update_table(self):
        if not self.selected_table_id:
            messagebox.showwarning("Chưa chọn bàn", "Vui lòng chọn một bàn để cập nhật.")
            return

        name = self.name_entry.get().strip()
        status = self.status_var.get()
        if not name:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập tên bàn.")
            return

        self.controller.edit_table(self.selected_table_id, name, status)
        self.load_tables()
        self.reset_form(show_message=False)

    def delete_table(self):
        if not self.selected_table_id:
            messagebox.showwarning("Chưa chọn bàn", "Vui lòng chọn một bàn để xóa.")
            return

        confirm = messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa bàn này?")
        if not confirm:
            return

        self.controller.remove_table(self.selected_table_id)
        self.load_tables()
        self.reset_form(show_message=False)

    def reset_form(self, show_message=True):
        self.selected_table_id = None
        self.name_entry.delete(0, tk.END)
        self.status_var.set("Trống")
        if show_message:
            messagebox.showinfo("Làm mới", "Đã xóa dữ liệu chọn bàn.")
