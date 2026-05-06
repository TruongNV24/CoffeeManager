import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

from Config.db import get_connection
from Views.theme import COLORS, FONT_FAMILY


class UserView:
    def __init__(self, parent):
        self.parent = parent
        self.selected_user_id = None
        self.employee_map = {}

        self.frame = tk.Frame(parent, bg=COLORS["app_bg"])
        self.frame.pack(fill="both", expand=True)

        self._build_ui()
        self._load_employees()
        self._load_users()

    def _build_ui(self):
        title = tk.Label(
            self.frame,
            text="Quản lý tài khoản & phân quyền",
            bg=COLORS["app_bg"],
            fg=COLORS["text"],
            font=(FONT_FAMILY, 18, "bold"),
        )
        title.pack(anchor="w", padx=16, pady=(12, 4))

        description = tk.Label(
            self.frame,
            text="Tạo tài khoản, đổi mật khẩu, phân quyền Admin/Staff và liên kết tài khoản với nhân viên.",
            bg=COLORS["app_bg"],
            fg=COLORS["muted"],
            font=(FONT_FAMILY, 10),
        )
        description.pack(anchor="w", padx=16, pady=(0, 8))

        form = tk.LabelFrame(
            self.frame, text="Thông tin tài khoản", bg=COLORS["surface"], padx=10, pady=8
        )
        form.pack(fill="x", padx=16, pady=(0, 10))

        tk.Label(form, text="Tên đăng nhập", bg=COLORS["surface"]).grid(
            row=0, column=0, sticky="w"
        )
        tk.Label(form, text="Mật khẩu", bg=COLORS["surface"]).grid(
            row=0, column=1, sticky="w", padx=(12, 0)
        )
        tk.Label(form, text="Quyền", bg=COLORS["surface"]).grid(
            row=0, column=2, sticky="w", padx=(12, 0)
        )
        tk.Label(form, text="Nhân viên", bg=COLORS["surface"]).grid(
            row=0, column=3, sticky="w", padx=(12, 0)
        )

        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.role_var = tk.StringVar(value="Staff")
        self.employee_var = tk.StringVar(value="Không liên kết")

        self.username_entry = tk.Entry(form, textvariable=self.username_var, width=22)
        self.username_entry.grid(row=1, column=0, pady=4)
        tk.Entry(form, textvariable=self.password_var, width=18, show="*").grid(
            row=1, column=1, padx=(12, 0), pady=4
        )
        self.role_combo = ttk.Combobox(
            form,
            textvariable=self.role_var,
            values=("Admin", "Staff"),
            width=12,
            state="readonly",
        )
        self.role_combo.grid(row=1, column=2, padx=(12, 0), pady=4)
        self.employee_combo = ttk.Combobox(
            form,
            textvariable=self.employee_var,
            width=32,
            state="readonly",
        )
        self.employee_combo.grid(row=1, column=3, padx=(12, 0), pady=4)

        action = tk.Frame(form, bg=COLORS["surface"])
        action.grid(row=2, column=0, columnspan=4, sticky="w", pady=(8, 0))
        tk.Button(
            action, text="Thêm", bg=COLORS["success"], fg="white", command=self._add_user
        ).pack(side="left", padx=(0, 6))
        tk.Button(
            action, text="Cập nhật", bg=COLORS["info"], fg="white", command=self._update_user
        ).pack(side="left", padx=6)
        tk.Button(
            action, text="Xóa", bg=COLORS["danger"], fg="white", command=self._delete_user
        ).pack(side="left", padx=6)
        tk.Button(
            action, text="Làm mới", bg=COLORS["muted"], fg="white", command=self._refresh
        ).pack(side="left", padx=6)

        note = tk.Label(
            form,
            text="Ghi chú: Khi cập nhật, để trống mật khẩu nếu không muốn đổi mật khẩu hiện tại.",
            bg=COLORS["surface"],
            fg=COLORS["muted"],
            font=(FONT_FAMILY, 9, "italic"),
        )
        note.grid(row=3, column=0, columnspan=4, sticky="w", pady=(8, 0))

        self.user_tree = ttk.Treeview(
            self.frame,
            columns=("id", "username", "role", "employee"),
            show="headings",
            height=15,
        )
        for col, text, width in [
            ("id", "ID", 60),
            ("username", "Tên đăng nhập", 190),
            ("role", "Quyền", 110),
            ("employee", "Nhân viên liên kết", 280),
        ]:
            self.user_tree.heading(col, text=text)
            self.user_tree.column(col, width=width)
        self.user_tree.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        self.user_tree.bind("<<TreeviewSelect>>", self._on_user_select)

    def _load_employees(self):
        conn = get_connection()
        rows = conn.execute(
            """
            SELECT EmployeeID, FullName
            FROM Employees
            ORDER BY FullName
            """
        ).fetchall()
        conn.close()

        self.employee_map = {"Không liên kết": None}
        for employee_id, full_name in rows:
            self.employee_map[f"{employee_id} - {full_name}"] = employee_id

        self.employee_combo["values"] = list(self.employee_map.keys())
        if self.employee_var.get() not in self.employee_map:
            self.employee_var.set("Không liên kết")

    def _load_users(self):
        for item in self.user_tree.get_children():
            self.user_tree.delete(item)

        conn = get_connection()
        rows = conn.execute(
            """
            SELECT u.UserID, u.Username, u.Role, IFNULL(e.FullName, 'Không liên kết')
            FROM Users u
            LEFT JOIN Employees e ON u.EmployeeID = e.EmployeeID
            ORDER BY u.UserID DESC
            """
        ).fetchall()
        conn.close()

        for row in rows:
            self.user_tree.insert("", "end", values=row)

    def _on_user_select(self, _event):
        selected = self.user_tree.selection()
        if not selected:
            return

        values = self.user_tree.item(selected[0], "values")
        self.selected_user_id = int(values[0])
        self.username_var.set(values[1])
        self.password_var.set("")
        self.role_var.set(values[2])
        self.username_entry.config(state="disabled")

        employee_key = self._get_employee_key(self.selected_user_id)
        self.employee_var.set(employee_key)

    def _get_employee_key(self, user_id):
        conn = get_connection()
        row = conn.execute(
            """
            SELECT e.EmployeeID, e.FullName
            FROM Users u
            LEFT JOIN Employees e ON u.EmployeeID = e.EmployeeID
            WHERE u.UserID = ?
            """,
            (user_id,),
        ).fetchone()
        conn.close()

        if not row or row[0] is None:
            return "Không liên kết"
        key = f"{row[0]} - {row[1]}"
        return key if key in self.employee_map else "Không liên kết"

    def _add_user(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        role = self.role_var.get().strip()
        employee_id = self.employee_map.get(self.employee_var.get(), None)

        if not username or not password:
            messagebox.showwarning(
                "Thiếu dữ liệu", "Vui lòng nhập tên đăng nhập và mật khẩu"
            )
            return
        if role not in ("Admin", "Staff"):
            messagebox.showwarning("Sai dữ liệu", "Quyền phải là Admin hoặc Staff")
            return

        conn = get_connection()
        try:
            conn.execute(
                "INSERT INTO Users (Username, Password, Role, EmployeeID) VALUES (?, ?, ?, ?)",
                (username, password, role, employee_id),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            messagebox.showerror("Không thể thêm", "Tên đăng nhập đã tồn tại")
            return
        except Exception as exc:
            messagebox.showerror("Không thể thêm", f"Không thể tạo tài khoản: {exc}")
            return
        finally:
            conn.close()

        self._clear_form()
        self._load_users()
        messagebox.showinfo("Thành công", "Đã thêm tài khoản")

    def _update_user(self):
        if not self.selected_user_id:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn tài khoản để cập nhật")
            return

        role = self.role_var.get().strip()
        if role not in ("Admin", "Staff"):
            messagebox.showwarning("Sai dữ liệu", "Quyền phải là Admin hoặc Staff")
            return

        if not self._can_change_admin_role(role):
            return

        password = self.password_var.get().strip()
        employee_id = self.employee_map.get(self.employee_var.get(), None)

        conn = get_connection()
        try:
            if password:
                conn.execute(
                    "UPDATE Users SET Password = ?, Role = ?, EmployeeID = ? WHERE UserID = ?",
                    (password, role, employee_id, self.selected_user_id),
                )
            else:
                conn.execute(
                    "UPDATE Users SET Role = ?, EmployeeID = ? WHERE UserID = ?",
                    (role, employee_id, self.selected_user_id),
                )
            conn.commit()
        except Exception as exc:
            messagebox.showerror(
                "Không thể cập nhật", f"Không thể cập nhật tài khoản: {exc}"
            )
            return
        finally:
            conn.close()

        self._clear_form()
        self._load_users()
        messagebox.showinfo("Thành công", "Đã cập nhật tài khoản")

    def _delete_user(self):
        if not self.selected_user_id:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn tài khoản để xóa")
            return

        if not self._can_delete_user():
            return

        username = self.username_var.get().strip()
        if not messagebox.askyesno(
            "Xác nhận", f"Bạn có chắc muốn xóa tài khoản '{username}'?"
        ):
            return

        conn = get_connection()
        try:
            conn.execute("DELETE FROM Users WHERE UserID = ?", (self.selected_user_id,))
            conn.commit()
        except Exception as exc:
            messagebox.showerror("Không thể xóa", f"Không thể xóa tài khoản: {exc}")
            return
        finally:
            conn.close()

        self._clear_form()
        self._load_users()
        messagebox.showinfo("Thành công", "Đã xóa tài khoản")

    def _refresh(self):
        self._clear_form()
        self._load_employees()
        self._load_users()

    def _can_change_admin_role(self, new_role):
        conn = get_connection()
        row = conn.execute(
            "SELECT Role FROM Users WHERE UserID = ?",
            (self.selected_user_id,),
        ).fetchone()
        admin_count = conn.execute(
            "SELECT COUNT(*) FROM Users WHERE Role = 'Admin'"
        ).fetchone()[0]
        conn.close()

        current_role = row[0] if row else None
        if current_role == "Admin" and new_role != "Admin" and admin_count <= 1:
            messagebox.showwarning(
                "Không thể đổi quyền",
                "Hệ thống phải có ít nhất một tài khoản Admin.",
            )
            return False
        return True

    def _can_delete_user(self):
        conn = get_connection()
        row = conn.execute(
            "SELECT Role FROM Users WHERE UserID = ?",
            (self.selected_user_id,),
        ).fetchone()
        admin_count = conn.execute(
            "SELECT COUNT(*) FROM Users WHERE Role = 'Admin'"
        ).fetchone()[0]
        user_count = conn.execute("SELECT COUNT(*) FROM Users").fetchone()[0]
        conn.close()

        if user_count <= 1:
            messagebox.showwarning(
                "Không thể xóa",
                "Hệ thống phải còn ít nhất một tài khoản để đăng nhập.",
            )
            return False
        if row and row[0] == "Admin" and admin_count <= 1:
            messagebox.showwarning(
                "Không thể xóa",
                "Hệ thống phải có ít nhất một tài khoản Admin.",
            )
            return False
        return True

    def _clear_form(self):
        self.selected_user_id = None
        self.username_entry.config(state="normal")
        self.username_var.set("")
        self.password_var.set("")
        self.role_var.set("Staff")
        self.employee_var.set("Không liên kết")
        self.user_tree.selection_remove(self.user_tree.selection())
