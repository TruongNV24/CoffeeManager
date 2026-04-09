from Config.db import get_connection, db_cloud

class MainController:
    def __init__(self, content_view):
        self.content_view = content_view

    # --- HÀM HỖ TRỢ ĐỒNG BỘ (SẼ DÙNG CHUNG) ---
    def sync_to_firebase(self, collection_name, document_id, data):
        """Đẩy dữ liệu lên Firebase và cập nhật lại SQLite"""
        if db_cloud:
            try:
                db_cloud.collection(collection_name).document(str(document_id)).set(data)
                return True
            except Exception as e:
                print(f"Lỗi đồng bộ Firebase: {e}")
        return False

    # --- CÁC HÀM HIỂN THỊ ---

    def show_tables(self):
        # Logic: Lấy danh sách bàn từ SQLite để hiện lên View
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Tables")
        tables = cursor.fetchall()
        conn.close()
        
        # Truyền dữ liệu sang View (giả sử content_view có hàm update_display)
        self.content_view.show_text(f"🪑 Quản lý bàn ({len(tables)} bàn)")

    def show_products(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Products")
        products = cursor.fetchall()
        conn.close()
        self.content_view.show_text(f"☕ Danh mục món ({len(products)} món)")

    def show_employees(self):
        # Ví dụ: Khi xem nhân viên, ta có thể kiểm tra xem ai chưa được đồng bộ
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Employees WHERE IsSynced = 0")
        unsynced = cursor.fetchall()
        conn.close()
        
        msg = "👨‍💼 Quản lý nhân viên"
        if unsynced:
            msg += f" (Có {len(unsynced)} người chưa đồng bộ mây)"
        self.content_view.show_text(msg)

    # Các hàm khác tương tự...
    def show_salary(self):
        self.content_view.show_text("💰 Quản lý Lương & Công")

    def show_users(self):
        self.content_view.show_text("🔐 Quản lý Tài khoản & Phân quyền")

    # --- VÍ DỤ: HÀM THANH TOÁN (ORDER) ---
    def create_order(self, table_id, employee_id, total_amount):
        conn = get_connection()
        cursor = conn.cursor()
        
        # 1. Lưu SQLite
        cursor.execute("""
            INSERT INTO Orders (TableID, EmployeeID, TotalAmount, IsSynced) 
            VALUES (?, ?, ?, 0)
        """, (table_id, employee_id, total_amount))
        
        order_id = cursor.lastrowid
        conn.commit()

        # 2. Thử đồng bộ lên Firebase ngay lập tức
        order_data = {
            "table_id": table_id,
            "employee_id": employee_id,
            "total": total_amount,
            "date": "2026-04-09" # Nên dùng datetime thật
        }
        
        if self.sync_to_firebase("orders", order_id, order_data):
            cursor.execute("UPDATE Orders SET IsSynced = 1 WHERE OrderID = ?", (order_id,))
            conn.commit()
            
        conn.close()