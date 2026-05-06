import tkinter as tk

from Config.db import create_tables, get_connection
from Controllers.Main import MainController
from Views.auth import AuthView
from Views.content import ContentView
from Views.header import HeaderView
from Views.menu import create_menu
from Views.theme import configure_root


def ensure_default_admin():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM Users")
    users_count = cursor.fetchone()[0]

    if users_count == 0:
        cursor.execute(
            "INSERT INTO Users (Username, Password, Role) VALUES ('admin', 'admin123', 'Admin')"
        )
        conn.commit()

    conn.close()


class CoffeeManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Coffee Manager - Hệ thống quản lý quán Cà phê")
        self.root.geometry("1180x760")
        self.root.minsize(1050, 680)
        configure_root(self.root)

        self.auth_view = None
        self.current_views = []

        self.show_auth()

    def clear_main_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_auth(self):
        self.clear_main_ui()
        self.auth_view = AuthView(self.root, self.show_dashboard)

    def show_dashboard(self, username, role):
        self.clear_main_ui()

        HeaderView(self.root, username=username, role=role, on_logout=self.show_auth)
        content_view = ContentView(self.root)
        controller = MainController(content_view, role=role)
        create_menu(self.root, controller, role=role)
        content_view.show_text(
            f"Xin chào {username}!",
            subtitle=f"Bạn đang đăng nhập với quyền {role}. Chọn chức năng ở menu bên trái để bắt đầu phục vụ khách hàng."
        )


def main():
    try:
        create_tables()
        ensure_default_admin()
        print("Database SQLite đã sẵn sàng.")
    except Exception as e:
        print(f"Lỗi khởi tạo database: {e}")

    root = tk.Tk()
    CoffeeManagerApp(root)

    print("Ứng dụng đang khởi chạy...")
    root.mainloop()


if __name__ == "__main__":
    main()
