import tkinter as tk
from tkinter import messagebox, ttk

from Config.db import get_connection
from Views.theme import COLORS, FONT_FAMILY


class EmployeeView:
    def __init__(self, parent):
        self.parent = parent
        self.selected_employee_id = None

        self.frame = tk.Frame(parent, bg=COLORS["app_bg"])
        self.frame.pack(fill="both", expand=True)

        self._build_ui()
        self.position_map = {}
        self._load_positions()
        self._load_employees()

    def _build_ui(self):
        title = tk.Label(
            self.frame,
            text="Quản lý nhân viên",
            bg=COLORS["app_bg"],
            fg=COLORS["text"],
            font=(FONT_FAMILY, 18, "bold"),
        )
        title.pack(anchor="w", padx=16, pady=(12, 8))

        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        self._build_employee_tab()

    def _build_employee_tab(self):
        tab = tk.Frame(self.notebook, bg=COLORS["surface"])
        self.notebook.add(tab, text="Nhân viên")

        form = tk.Frame(tab, bg=COLORS["surface"])
        form.pack(fill="x", padx=8, pady=8)

        tk.Label(form, text="Họ tên", bg=COLORS["surface"]).grid(row=0, column=0, sticky="w")
        tk.Label(form, text="SĐT", bg=COLORS["surface"]).grid(row=0, column=1, sticky="w", padx=(12, 0))
        tk.Label(form, text="Vị trí", bg=COLORS["surface"]).grid(row=0, column=2, sticky="w", padx=(12, 0))

        self.emp_name = tk.StringVar()
        self.emp_phone = tk.StringVar()
        self.emp_position = tk.StringVar()

        tk.Entry(form, textvariable=self.emp_name, width=28).grid(row=1, column=0, pady=4)
        tk.Entry(form, textvariable=self.emp_phone, width=18).grid(row=1, column=1, padx=(12, 0), pady=4)
        self.position_combo = ttk.Combobox(form, textvariable=self.emp_position, width=18, state="readonly")
        self.position_combo.grid(row=1, column=2, padx=(12, 0), pady=4)

        action = tk.Frame(form, bg=COLORS["surface"])
        action.grid(row=1, column=3, padx=16)
        tk.Button(action, text="Thêm", bg=COLORS["success"], fg="white", command=self._add_employee).pack(side="left", padx=3)
        tk.Button(action, text="Cập nhật", bg=COLORS["info"], fg="white", command=self._update_employee).pack(side="left", padx=3)
        tk.Button(action, text="Xóa", bg=COLORS["danger"], fg="white", command=self._delete_employee).pack(side="left", padx=3)

        self.employee_tree = ttk.Treeview(tab, columns=("id", "name", "phone", "position"), show="headings", height=14)
        for col, text, width in [
            ("id", "ID", 50),
            ("name", "Họ tên", 250),
            ("phone", "SĐT", 140),
            ("position", "Vị trí", 160),
        ]:
            self.employee_tree.heading(col, text=text)
            self.employee_tree.column(col, width=width)
        self.employee_tree.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self.employee_tree.bind("<<TreeviewSelect>>", self._on_employee_select)

    def _build_shift_tab(self):
        tab = tk.Frame(self.notebook, bg=COLORS["surface"])
        self.notebook.add(tab, text="Ca làm")

        form = tk.Frame(tab, bg=COLORS["surface"])
        form.pack(fill="x", padx=8, pady=8)

        tk.Label(form, text="Nhân viên (ID)", bg=COLORS["surface"]).grid(row=0, column=0, sticky="w")
        tk.Label(form, text="Ngày (YYYY-MM-DD)", bg=COLORS["surface"]).grid(row=0, column=1, sticky="w", padx=(12, 0))
        tk.Label(form, text="Giờ bắt đầu", bg=COLORS["surface"]).grid(row=0, column=2, sticky="w", padx=(12, 0))
        tk.Label(form, text="Giờ kết thúc", bg=COLORS["surface"]).grid(row=0, column=3, sticky="w", padx=(12, 0))

        self.shift_emp_id = tk.StringVar()
        self.shift_date = tk.StringVar()
        self.shift_start = tk.StringVar(value="08:00")
        self.shift_end = tk.StringVar(value="17:00")

        tk.Entry(form, textvariable=self.shift_emp_id, width=15).grid(row=1, column=0, pady=4)
        tk.Entry(form, textvariable=self.shift_date, width=16).grid(row=1, column=1, padx=(12, 0), pady=4)
        tk.Entry(form, textvariable=self.shift_start, width=10).grid(row=1, column=2, padx=(12, 0), pady=4)
        tk.Entry(form, textvariable=self.shift_end, width=10).grid(row=1, column=3, padx=(12, 0), pady=4)
        tk.Button(form, text="Tạo ca", bg=COLORS["success"], fg="white", command=self._add_shift).grid(row=1, column=4, padx=16)

        self.shift_tree = ttk.Treeview(tab, columns=("id", "emp", "date", "start", "end"), show="headings", height=14)
        for col, text, width in [
            ("id", "ShiftID", 70),
            ("emp", "Nhân viên", 120),
            ("date", "Ngày", 130),
            ("start", "Bắt đầu", 120),
            ("end", "Kết thúc", 120),
        ]:
            self.shift_tree.heading(col, text=text)
            self.shift_tree.column(col, width=width)
        self.shift_tree.pack(fill="both", expand=True, padx=8, pady=(0, 8))

    def _build_attendance_tab(self):
        tab = tk.Frame(self.notebook, bg=COLORS["surface"])
        self.notebook.add(tab, text="Chấm công")

        form = tk.Frame(tab, bg=COLORS["surface"])
        form.pack(fill="x", padx=8, pady=8)

        tk.Label(form, text="ShiftID", bg=COLORS["surface"]).grid(row=0, column=0, sticky="w")
        tk.Label(form, text="Trạng thái", bg=COLORS["surface"]).grid(row=0, column=1, sticky="w", padx=(12, 0))

        self.att_shift_id = tk.StringVar()
        self.att_status = tk.StringVar(value="Có mặt")

        tk.Entry(form, textvariable=self.att_shift_id, width=12).grid(row=1, column=0, pady=4)
        tk.OptionMenu(form, self.att_status, "Có mặt", "Đi trễ", "Vắng").grid(row=1, column=1, padx=(12, 0), pady=4)
        tk.Button(form, text="Chấm công", bg=COLORS["primary_dark"], fg="white", command=self._mark_attendance).grid(row=1, column=2, padx=16)

        self.attendance_tree = ttk.Treeview(tab, columns=("id", "shift", "checkin", "status"), show="headings", height=14)
        for col, text, width in [
            ("id", "ID", 70),
            ("shift", "ShiftID", 80),
            ("checkin", "Thời gian", 190),
            ("status", "Trạng thái", 130),
        ]:
            self.attendance_tree.heading(col, text=text)
            self.attendance_tree.column(col, width=width)
        self.attendance_tree.pack(fill="both", expand=True, padx=8, pady=(0, 8))


    def _load_positions(self):
        conn = get_connection()
        rows = conn.execute(
            "SELECT PositionID, PositionName FROM Positions ORDER BY PositionName"
        ).fetchall()
        conn.close()

        self.position_map = {row[1]: row[0] for row in rows}
        self.position_combo["values"] = list(self.position_map.keys())
        if self.position_map and not self.emp_position.get():
            self.emp_position.set(next(iter(self.position_map.keys())))

    def _load_employees(self):
        for item in self.employee_tree.get_children():
            self.employee_tree.delete(item)
        conn = get_connection()
        rows = conn.execute(
            """
            SELECT e.EmployeeID, e.FullName, IFNULL(e.Phone, ''), IFNULL(p.PositionName, '')
            FROM Employees e
            LEFT JOIN Positions p ON e.PositionID = p.PositionID
            ORDER BY e.EmployeeID DESC
            """
        ).fetchall()
        conn.close()
        for row in rows:
            self.employee_tree.insert("", "end", values=row)

    def _load_shifts(self):
        for item in self.shift_tree.get_children():
            self.shift_tree.delete(item)
        conn = get_connection()
        rows = conn.execute(
            """
            SELECT ShiftID, EmployeeID, ShiftDate, StartTime, EndTime
            FROM WorkShifts
            ORDER BY ShiftDate DESC, ShiftID DESC
            """
        ).fetchall()
        conn.close()
        for row in rows:
            self.shift_tree.insert("", "end", values=row)

    def _load_attendance(self):
        for item in self.attendance_tree.get_children():
            self.attendance_tree.delete(item)
        conn = get_connection()
        rows = conn.execute(
            """
            SELECT AttendanceID, ShiftID, CheckInTime, Status
            FROM Attendance
            ORDER BY AttendanceID DESC
            """
        ).fetchall()
        conn.close()
        for row in rows:
            self.attendance_tree.insert("", "end", values=row)

    def _on_employee_select(self, _event):
        selected = self.employee_tree.selection()
        if not selected:
            return
        values = self.employee_tree.item(selected[0], "values")
        self.selected_employee_id = int(values[0])
        self.emp_name.set(values[1])
        self.emp_phone.set(values[2])
        self.emp_position.set(values[3])

    def _add_employee(self):
        name = self.emp_name.get().strip()
        if not name:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập họ tên nhân viên")
            return
        position_name = self.emp_position.get().strip()
        position_id = self.position_map.get(position_name)
        if not position_id:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng chọn vị trí hợp lệ từ danh sách")
            return

        conn = get_connection()
        conn.execute(
            "INSERT INTO Employees (FullName, Phone, PositionID, IsSynced) VALUES (?, ?, ?, 0)",
            (name, self.emp_phone.get().strip(), position_id),
        )
        conn.commit()
        conn.close()
        self._load_employees()

    def _update_employee(self):
        if not self.selected_employee_id:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn nhân viên để cập nhật")
            return
        name = self.emp_name.get().strip()
        if not name:
            messagebox.showwarning("Thiếu dữ liệu", "Tên nhân viên không được để trống")
            return
        position_id = self.position_map.get(self.emp_position.get().strip())
        if not position_id:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng chọn vị trí hợp lệ từ danh sách")
            return

        conn = get_connection()
        conn.execute(
            "UPDATE Employees SET FullName=?, Phone=?, PositionID=?, IsSynced=0 WHERE EmployeeID=?",
            (name, self.emp_phone.get().strip(), position_id, self.selected_employee_id),
        )
        conn.commit()
        conn.close()
        self._load_employees()

    def _delete_employee(self):
        if not self.selected_employee_id:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn nhân viên để xóa")
            return
        if not messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa nhân viên này?"):
            return
        conn = get_connection()
        try:
            conn.execute("DELETE FROM Employees WHERE EmployeeID=?", (self.selected_employee_id,))
            conn.commit()
        except Exception as e:
            messagebox.showerror("Không thể xóa", f"Nhân viên đang có dữ liệu liên quan.\n{e}")
        finally:
            conn.close()
        self.selected_employee_id = None
        self._load_employees()

    def _add_shift(self):
        try:
            employee_id = int(self.shift_emp_id.get().strip())
        except ValueError:
            messagebox.showwarning("Sai dữ liệu", "EmployeeID phải là số")
            return

        shift_date = self.shift_date.get().strip()
        if not shift_date:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập ngày ca làm")
            return

        conn = get_connection()
        conn.execute(
            """
            INSERT INTO WorkShifts (EmployeeID, ShiftDate, StartTime, EndTime)
            VALUES (?, ?, ?, ?)
            """,
            (employee_id, shift_date, self.shift_start.get().strip(), self.shift_end.get().strip()),
        )
        conn.commit()
        conn.close()
        self._load_shifts()

    def _mark_attendance(self):
        try:
            shift_id = int(self.att_shift_id.get().strip())
        except ValueError:
            messagebox.showwarning("Sai dữ liệu", "ShiftID phải là số")
            return

        conn = get_connection()
        conn.execute(
            "INSERT INTO Attendance (ShiftID, Status) VALUES (?, ?)",
            (shift_id, self.att_status.get()),
        )
        conn.commit()
        conn.close()
        self._load_attendance()
