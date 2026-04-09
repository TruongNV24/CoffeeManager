import tkinter as tk
from Views.header import HeaderView
from Views.menu import create_menu
from Views.content import ContentView
from Controllers.Main import MainController
# Import thêm Config để khởi tạo database
from Config.db import create_tables

def main():

    try:
        create_tables()
        print("Database SQLite đã sẵn sàng.")
    except Exception as e:
        print(f"Lỗi khởi tạo database: {e}")

    root = tk.Tk()
    root.title("Coffee Manager - Hệ thống quản lý quán Cà phê")
    root.geometry("1100x700")


    HeaderView(root, "Quản trị viên")

    content_view = ContentView(root)


    controller = MainController(content_view)

    create_menu(root, controller)

    print("Ứng dụng đang khởi chạy...")
    root.mainloop()

if __name__ == "__main__":
    main()