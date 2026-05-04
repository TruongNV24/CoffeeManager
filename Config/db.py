import sqlite3
import firebase_admin
from firebase_admin import credentials, firestore

DB_NAME = "database.db"

def init_firebase():
    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate("serviceAccountKey.json")
            firebase_admin.initialize_app(cred)
        return firestore.client()
    except Exception as e:
        print(f"Không thể kết nối Firebase: {e}")
        return None

# Biến toàn cục để dùng ở các file Controller
db_cloud = init_firebase()

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Positions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Positions (
        PositionID INTEGER PRIMARY KEY AUTOINCREMENT,
        PositionName TEXT NOT NULL,
        BaseSalary REAL NOT NULL
    )""")

    # 2. Employees (Thêm IsSynced để quản lý nhân sự từ xa)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Employees (
        EmployeeID INTEGER PRIMARY KEY AUTOINCREMENT,
        FullName TEXT NOT NULL,
        Gender TEXT,
        DateOfBirth TEXT,
        Phone TEXT,
        Email TEXT,
        Address TEXT,
        PositionID INTEGER,
        Status TEXT DEFAULT 'Đang làm',
        IsSynced INTEGER DEFAULT 0, 
        FOREIGN KEY (PositionID) REFERENCES Positions(PositionID)
    )""")

    # 3. Users
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Users (
        UserID INTEGER PRIMARY KEY AUTOINCREMENT,
        Username TEXT UNIQUE NOT NULL,
        Password TEXT NOT NULL,
        Role TEXT CHECK(Role IN ('Admin', 'Staff')) NOT NULL,
        EmployeeID INTEGER,
        FOREIGN KEY (EmployeeID) REFERENCES Employees(EmployeeID)
    )""")

    # 4. Tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Tables (
        TableID INTEGER PRIMARY KEY AUTOINCREMENT,
        TableName TEXT,
        Status TEXT DEFAULT 'Trống'
    )""")

    # 5. Categories
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Categories (
        CategoryID INTEGER PRIMARY KEY AUTOINCREMENT,
        CategoryName TEXT NOT NULL
    )""")

    # 6. Products (Thêm IsSynced để đồng bộ menu)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Products (
        ProductID INTEGER PRIMARY KEY AUTOINCREMENT,
        ProductName TEXT NOT NULL,
        CategoryID INTEGER,
        Price REAL NOT NULL,
        Status TEXT DEFAULT 'Còn bán',
        ProductImage TEXT,
        IsSynced INTEGER DEFAULT 0,
        FOREIGN KEY (CategoryID) REFERENCES Categories(CategoryID)
    )""")

    # Migration cho DB cũ chưa có cột ProductImage
    cursor.execute("PRAGMA table_info(Products)")
    product_columns = [col[1] for col in cursor.fetchall()]
    if "ProductImage" not in product_columns:
        cursor.execute("ALTER TABLE Products ADD COLUMN ProductImage TEXT")

    # 7. Orders (QUAN TRỌNG: Cần đồng bộ để chủ quán xem doanh thu)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Orders (
        OrderID INTEGER PRIMARY KEY AUTOINCREMENT,
        TableID INTEGER,
        EmployeeID INTEGER,
        OrderDate TEXT DEFAULT CURRENT_TIMESTAMP,
        TotalAmount REAL DEFAULT 0,
        Status TEXT DEFAULT 'Đang dùng',
        IsSynced INTEGER DEFAULT 0,
        FOREIGN KEY (TableID) REFERENCES Tables(TableID),
        FOREIGN KEY (EmployeeID) REFERENCES Employees(EmployeeID)
    )""")

    # 8. OrderDetails
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS OrderDetails (
        OrderDetailID INTEGER PRIMARY KEY AUTOINCREMENT,
        OrderID INTEGER,
        ProductID INTEGER,
        Quantity INTEGER NOT NULL,
        Price REAL NOT NULL,
        SubTotal REAL,
        FOREIGN KEY (OrderID) REFERENCES Orders(OrderID),
        FOREIGN KEY (ProductID) REFERENCES Products(ProductID)
    )""")

    # 9. Salaries
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Salaries (
        SalaryID INTEGER PRIMARY KEY AUTOINCREMENT,
        EmployeeID INTEGER NOT NULL,
        Month TEXT NOT NULL,
        WorkDays INTEGER DEFAULT 0,
        Bonus REAL DEFAULT 0,
        TotalSalary REAL,
        IsSynced INTEGER DEFAULT 0,
        FOREIGN KEY (EmployeeID) REFERENCES Employees(EmployeeID)
    )""")


    # 10. WorkShifts
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS WorkShifts (
        ShiftID INTEGER PRIMARY KEY AUTOINCREMENT,
        EmployeeID INTEGER NOT NULL,
        ShiftDate TEXT NOT NULL,
        StartTime TEXT NOT NULL,
        EndTime TEXT NOT NULL,
        FOREIGN KEY (EmployeeID) REFERENCES Employees(EmployeeID)
    )""")

    # 11. Attendance
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Attendance (
        AttendanceID INTEGER PRIMARY KEY AUTOINCREMENT,
        ShiftID INTEGER NOT NULL,
        CheckInTime TEXT DEFAULT CURRENT_TIMESTAMP,
        Status TEXT CHECK(Status IN ('Có mặt', 'Đi trễ', 'Vắng')) DEFAULT 'Có mặt',
        FOREIGN KEY (ShiftID) REFERENCES WorkShifts(ShiftID)
    )""")
    conn.commit()
    conn.close()
