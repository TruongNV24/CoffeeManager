import tkinter as tk
from tkinter import messagebox, ttk

from Config.db import get_connection


class SalaryView:
    def __init__(self, parent):
        self.parent = parent
        self.selected_position_id = None

        self.frame = tk.Frame(parent, bg="white")
        self.frame.pack(fill="both", expand=True)

        self._build_ui()
        self._load_positions()
        self._load_salaries()

    def _build_ui(self):
        title = tk.Label(
            self.frame,
            text="Quản lý lương nhân viên",
            bg="white",
            fg="#2c3e50",
            font=("Arial", 15, "bold"),
        )
        title.pack(anchor="w", padx=16, pady=(12, 8))

        notebook = ttk.Notebook(self.frame)
        notebook.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        self._build_position_tab(notebook)
        self._build_salary_tab(notebook)

    def _build_position_tab(self, notebook):
        tab = tk.Frame(notebook, bg="white")
        notebook.add(tab, text="Tạo vị trí & lương cơ bản")

        form = tk.Frame(tab, bg="white")
        form.pack(fill="x", padx=8, pady=8)

        tk.Label(form, text="Tên vị trí", bg="white").grid(row=0, column=0, sticky="w")
        tk.Label(form, text="Lương cơ bản", bg="white").grid(row=0, column=1, sticky="w", padx=(12, 0))

        self.position_name = tk.StringVar()
        self.base_salary = tk.StringVar(value="0")

        tk.Entry(form, textvariable=self.position_name, width=28).grid(row=1, column=0, pady=4)
        tk.Entry(form, textvariable=self.base_salary, width=16).grid(row=1, column=1, padx=(12, 0), pady=4)

        action = tk.Frame(form, bg="white")
        action.grid(row=1, column=2, padx=16)
        tk.Button(action, text="Thêm", bg="#2ecc71", fg="white", command=self._add_position).pack(side="left", padx=3)
        tk.Button(action, text="Cập nhật", bg="#3498db", fg="white", command=self._update_position).pack(side="left", padx=3)

        self.position_tree = ttk.Treeview(tab, columns=("id", "name", "salary"), show="headings", height=14)
        for col, text, width in [
            ("id", "ID", 60),
            ("name", "Vị trí", 220),
            ("salary", "Lương cơ bản", 160),
        ]:
            self.position_tree.heading(col, text=text)
            self.position_tree.column(col, width=width)
        self.position_tree.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self.position_tree.bind("<<TreeviewSelect>>", self._on_position_select)

    def _build_salary_tab(self, notebook):
        tab = tk.Frame(notebook, bg="white")
        notebook.add(tab, text="Bảng lương")

        form = tk.Frame(tab, bg="white")
        form.pack(fill="x", padx=8, pady=8)

        tk.Label(form, text="Nhân viên", bg="white").grid(row=0, column=0, sticky="w")
        tk.Label(form, text="Tháng (YYYY-MM)", bg="white").grid(row=0, column=1, sticky="w", padx=(12, 0))
        tk.Label(form, text="Số ngày công", bg="white").grid(row=0, column=2, sticky="w", padx=(12, 0))
        tk.Label(form, text="Thưởng/Phạt", bg="white").grid(row=0, column=3, sticky="w", padx=(12, 0))

        self.salary_employee = tk.StringVar()
        self.salary_month = tk.StringVar()
        self.salary_work_days = tk.StringVar(value="26")
        self.salary_bonus = tk.StringVar(value="0")

        self.employee_combo = ttk.Combobox(form, textvariable=self.salary_employee, width=30, state="readonly")
        self.employee_combo.grid(row=1, column=0, pady=4)
        tk.Entry(form, textvariable=self.salary_month, width=14).grid(row=1, column=1, padx=(12, 0), pady=4)
        tk.Entry(form, textvariable=self.salary_work_days, width=12).grid(row=1, column=2, padx=(12, 0), pady=4)
        tk.Entry(form, textvariable=self.salary_bonus, width=14).grid(row=1, column=3, padx=(12, 0), pady=4)
        tk.Button(form, text="Lưu bảng lương", bg="#16a085", fg="white", command=self._save_salary).grid(row=1, column=4, padx=16)

        self.salary_tree = ttk.Treeview(
            tab,
            columns=("id", "emp", "position", "month", "base", "workdays", "bonus", "total"),
            show="headings",
            height=14,
        )
        for col, text, width in [
            ("id", "ID", 50),
            ("emp", "Nhân viên", 170),
            ("position", "Vị trí", 120),
            ("month", "Tháng", 90),
            ("base", "Lương cơ bản", 120),
            ("workdays", "Ngày công", 85),
            ("bonus", "Thưởng/Phạt", 110),
            ("total", "Tổng lương", 120),
        ]:
            self.salary_tree.heading(col, text=text)
            self.salary_tree.column(col, width=width)
        self.salary_tree.pack(fill="both", expand=True, padx=8, pady=(0, 8))

    def _load_positions(self):
        for item in self.position_tree.get_children():
            self.position_tree.delete(item)

        conn = get_connection()
        rows = conn.execute(
            "SELECT PositionID, PositionName, BaseSalary FROM Positions ORDER BY PositionName"
        ).fetchall()
        emp_rows = conn.execute(
            """
            SELECT e.EmployeeID, e.FullName, IFNULL(p.PositionName, 'Chưa có vị trí')
            FROM Employees e
            LEFT JOIN Positions p ON e.PositionID = p.PositionID
            ORDER BY e.FullName
            """
        ).fetchall()
        conn.close()

        for row in rows:
            self.position_tree.insert("", "end", values=row)

        self.employee_map = {f"{row[0]} - {row[1]} ({row[2]})": row[0] for row in emp_rows}
        self.employee_combo["values"] = list(self.employee_map.keys())
        if self.employee_map and not self.salary_employee.get():
            self.salary_employee.set(next(iter(self.employee_map.keys())))

    def _load_salaries(self):
        for item in self.salary_tree.get_children():
            self.salary_tree.delete(item)

        conn = get_connection()
        rows = conn.execute(
            """
            SELECT s.SalaryID, e.FullName, IFNULL(p.PositionName, ''), s.Month,
                   IFNULL(p.BaseSalary, 0), s.WorkDays, s.Bonus, s.TotalSalary
            FROM Salaries s
            JOIN Employees e ON s.EmployeeID = e.EmployeeID
            LEFT JOIN Positions p ON e.PositionID = p.PositionID
            ORDER BY s.Month DESC, s.SalaryID DESC
            """
        ).fetchall()
        conn.close()

        for row in rows:
            self.salary_tree.insert("", "end", values=row)

    def _on_position_select(self, _event):
        selected = self.position_tree.selection()
        if not selected:
            return
        values = self.position_tree.item(selected[0], "values")
        self.selected_position_id = int(values[0])
        self.position_name.set(values[1])
        self.base_salary.set(str(values[2]))

    def _add_position(self):
        name = self.position_name.get().strip()
        if not name:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập tên vị trí")
            return

        try:
            base = float(self.base_salary.get().strip() or 0)
        except ValueError:
            messagebox.showwarning("Sai dữ liệu", "Lương cơ bản phải là số")
            return

        conn = get_connection()
        conn.execute(
            "INSERT INTO Positions (PositionName, BaseSalary) VALUES (?, ?)",
            (name, base),
        )
        conn.commit()
        conn.close()
        self._load_positions()

    def _update_position(self):
        if not self.selected_position_id:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn vị trí để cập nhật")
            return

        try:
            base = float(self.base_salary.get().strip() or 0)
        except ValueError:
            messagebox.showwarning("Sai dữ liệu", "Lương cơ bản phải là số")
            return

        conn = get_connection()
        conn.execute(
            "UPDATE Positions SET PositionName=?, BaseSalary=? WHERE PositionID=?",
            (self.position_name.get().strip(), base, self.selected_position_id),
        )
        conn.commit()
        conn.close()
        self._load_positions()

    def _save_salary(self):
        employee_key = self.salary_employee.get().strip()
        if employee_key not in self.employee_map:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng chọn nhân viên")
            return

        month = self.salary_month.get().strip()
        if not month:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập tháng")
            return

        try:
            work_days = int(self.salary_work_days.get().strip() or 0)
            bonus = float(self.salary_bonus.get().strip() or 0)
        except ValueError:
            messagebox.showwarning("Sai dữ liệu", "Ngày công/thưởng phạt không hợp lệ")
            return

        employee_id = self.employee_map[employee_key]
        conn = get_connection()
        base_row = conn.execute(
            """
            SELECT IFNULL(p.BaseSalary, 0)
            FROM Employees e
            LEFT JOIN Positions p ON e.PositionID = p.PositionID
            WHERE e.EmployeeID = ?
            """,
            (employee_id,),
        ).fetchone()

        base_salary = float(base_row[0] if base_row else 0)
        total_salary = base_salary + bonus

        conn.execute(
            """
            INSERT INTO Salaries (EmployeeID, Month, WorkDays, Bonus, TotalSalary, IsSynced)
            VALUES (?, ?, ?, ?, ?, 0)
            """,
            (employee_id, month, work_days, bonus, total_salary),
        )
        conn.commit()
        conn.close()
        self._load_salaries()
