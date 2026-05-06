import tkinter as tk
from tkinter import messagebox

from Controllers.table import TableController
from Views.theme import COLORS, FONT_FAMILY, button, entry


class TableView:
    def __init__(self, parent, role):
        self.parent = parent
        self.role = role
        self.controller = TableController()
        self.selected_table_id = None

        self.frame = tk.Frame(parent, bg=COLORS["app_bg"])
        self.frame.pack(fill="both", expand=True)

        self.build_crud_panel()
        self.load_tables()

    def build_crud_panel(self):
        header = tk.Frame(self.frame, bg=COLORS["app_bg"])
        header.pack(fill="x", padx=24, pady=(20, 8))

        title_group = tk.Frame(header, bg=COLORS["app_bg"])
        title_group.pack(side="left", fill="x", expand=True)
        tk.Label(
            title_group,
            text="Sơ đồ bàn",
            bg=COLORS["app_bg"],
            fg=COLORS["text"],
            font=(FONT_FAMILY, 20, "bold"),
        ).pack(anchor="w")
        tk.Label(
            title_group,
            text="Theo dõi trạng thái và cập nhật bàn chỉ với một lần chọn.",
            bg=COLORS["app_bg"],
            fg=COLORS["muted"],
            font=(FONT_FAMILY, 10),
        ).pack(anchor="w", pady=(2, 0))

        self.crud_panel_visible = False
        self.crud_toggle_button = button(
            header,
            text="⚙️  Mở CRUD",
            variant="dark",
            command=self.toggle_crud_panel,
        )
        self.crud_toggle_button.pack(side="right", anchor="n", padx=(16, 0))

        form_frame = tk.Frame(
            self.frame,
            bg=COLORS["surface"],
            padx=18,
            pady=16,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
        )
        self.crud_panel = form_frame

        tk.Label(form_frame, text="Tên bàn", bg=COLORS["surface"], fg=COLORS["muted"], font=(FONT_FAMILY, 10, "bold")).grid(
            row=0, column=0, sticky="w", padx=(0, 8)
        )
        self.name_entry = entry(form_frame, width=24, font=(FONT_FAMILY, 11))
        self.name_entry.grid(row=1, column=0, sticky="w", ipady=7, padx=(0, 14))

        tk.Label(form_frame, text="Trạng thái", bg=COLORS["surface"], fg=COLORS["muted"], font=(FONT_FAMILY, 10, "bold")).grid(
            row=0, column=1, sticky="w", padx=(0, 8)
        )
        self.status_var = tk.StringVar(value="Trống")
        status_options = ("Trống", "Đang dùng")
        self.status_menu = tk.OptionMenu(form_frame, self.status_var, *status_options)
        self.status_menu.config(width=12, bg=COLORS["white"], fg=COLORS["text"], relief="flat", highlightthickness=1, highlightbackground=COLORS["border"])
        self.status_menu.grid(row=1, column=1, sticky="w", ipady=3)

        action_frame = tk.Frame(form_frame, bg=COLORS["surface"])
        action_frame.grid(row=1, column=2, padx=(24, 0))

        self.btn_add = button(action_frame, text="Thêm", variant="success", command=self.add_table)
        self.btn_add.pack(side="left", padx=4)
        self.btn_update = button(action_frame, text="Cập nhật", variant="info", command=self.update_table)
        self.btn_update.pack(side="left", padx=4)
        self.btn_delete = button(action_frame, text="Xóa", variant="danger", command=self.delete_table)
        self.btn_delete.pack(side="left", padx=4)
        button(action_frame, text="Làm mới", variant="ghost", command=self.reset_form).pack(side="left", padx=4)

        if self.role == "Staff":
            self.name_entry.config(state="disabled")
            self.btn_add.config(state="disabled")
            self.btn_delete.config(state="disabled")

        self.list_frame = tk.Frame(self.frame, bg=COLORS["app_bg"])
        self.list_frame.pack(fill="both", expand=True, padx=24, pady=(0, 24))


    def toggle_crud_panel(self):
        if self.crud_panel_visible:
            self.crud_panel.pack_forget()
            self.crud_toggle_button.config(text="⚙️  Mở CRUD")
            self.crud_panel_visible = False
            return

        self.crud_panel.pack(fill="x", padx=24, pady=(8, 16), before=self.list_frame)
        self.crud_toggle_button.config(text="Ẩn CRUD")
        self.crud_panel_visible = True

    def load_tables(self):
        tables = self.controller.load_tables()

        for widget in self.list_frame.winfo_children():
            widget.destroy()

        if not tables:
            tk.Label(
                self.list_frame,
                text="Chưa có bàn nào trong hệ thống.",
                bg=COLORS["app_bg"],
                fg=COLORS["muted"],
                font=(FONT_FAMILY, 12),
            ).pack(pady=40)
            return

        header_text = "Danh sách bàn (nhấn để chọn):"
        if self.role == "Staff":
            header_text += " Staff chỉ được đổi trạng thái."

        tk.Label(
            self.list_frame,
            text=header_text,
            bg=COLORS["app_bg"],
            fg=COLORS["text"],
            font=(FONT_FAMILY, 12, "bold"),
        ).pack(anchor="w", pady=(5, 12))

        grid_frame = tk.Frame(self.list_frame, bg=COLORS["app_bg"])
        grid_frame.pack(fill="both", expand=True)

        for index, table in enumerate(tables):
            name = table[1]
            status = table[2]
            is_empty = status == "Trống"
            color = "#e8f5ed" if is_empty else "#fff0e8"
            fg = COLORS["success"] if is_empty else COLORS["danger"]
            icon = "✅" if is_empty else "☕"

            btn = tk.Button(
                grid_frame,
                text=f"{icon}  {name}\n{status}",
                bg=color,
                fg=fg,
                activebackground=COLORS["border"],
                activeforeground=fg,
                relief="flat",
                bd=0,
                highlightthickness=1,
                highlightbackground=COLORS["border"],
                width=18,
                height=4,
                font=(FONT_FAMILY, 11, "bold"),
                cursor="hand2",
                command=lambda data=table: self.select_table(data),
            )

            btn.grid(row=index // 4, column=index % 4, padx=10, pady=10, sticky="nsew")

    def select_table(self, table):
        table_id, name, status = table
        self.selected_table_id = table_id
        self.name_entry.config(state="normal")
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, name or "")
        if self.role == "Staff":
            self.name_entry.config(state="disabled")
        self.status_var.set(status or "Trống")

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

        status = self.status_var.get()

        if self.role == "Staff":
            self.controller.update_table_status_only(self.selected_table_id, status)
        else:
            name = self.name_entry.get().strip()
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
        self.name_entry.config(state="normal")
        self.name_entry.delete(0, tk.END)
        if self.role == "Staff":
            self.name_entry.config(state="disabled")
        self.status_var.set("Trống")
        if show_message:
            messagebox.showinfo("Làm mới", "Đã xóa dữ liệu chọn bàn.")
