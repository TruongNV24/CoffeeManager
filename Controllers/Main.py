from Config.db import db_cloud, get_connection
from Views.order import OrderView
from Views.table import TableView
from Views.employee import EmployeeView


class MainController:
    def __init__(self, content_view, role):
        self.content_view = content_view
        self.role = role
        self.permissions = {
            "Admin": {
                "show_tables",
                "show_products",
                "show_employees",
                "show_salary",
                "show_users",
            },
            "Staff": {"show_tables", "show_products"},
        }

    def _can_access(self, action_name):
        return action_name in self.permissions.get(self.role, set())

    def _deny_access(self):
        self.content_view.show_text("⛔ Bạn không có quyền truy cập chức năng này.")

    def sync_to_firebase(self, collection_name, document_id, data):
        if db_cloud:
            try:
                db_cloud.collection(collection_name).document(str(document_id)).set(data)
                return True
            except Exception as e:
                print(f"Lỗi đồng bộ Firebase: {e}")
        return False

    def show_tables(self):
        if not self._can_access("show_tables"):
            self._deny_access()
            return

        self.content_view.clear()
        TableView(self.content_view.frame, role=self.role)

    def show_products(self):
        if not self._can_access("show_products"):
            self._deny_access()
            return

        self.content_view.clear()
        OrderView(self.content_view.frame, role=self.role)

    def show_employees(self):
        if not self._can_access("show_employees"):
            self._deny_access()
            return

        self.content_view.clear()
        EmployeeView(self.content_view.frame)

    def show_salary(self):
        if not self._can_access("show_salary"):
            self._deny_access()
            return

        self.content_view.show_text("💰 Quản lý Lương & Công")

    def show_users(self):
        if not self._can_access("show_users"):
            self._deny_access()
            return

        self.content_view.show_text("🔐 Quản lý Tài khoản & Phân quyền")

    def create_order(self, table_id, employee_id, total_amount):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO Orders (TableID, EmployeeID, TotalAmount, IsSynced)
            VALUES (?, ?, ?, 0)
        """,
            (table_id, employee_id, total_amount),
        )

        order_id = cursor.lastrowid
        conn.commit()

        order_data = {
            "table_id": table_id,
            "employee_id": employee_id,
            "total": total_amount,
            "date": "2026-04-14",
        }

        if self.sync_to_firebase("orders", order_id, order_data):
            cursor.execute("UPDATE Orders SET IsSynced = 1 WHERE OrderID = ?", (order_id,))
            conn.commit()

        conn.close()
