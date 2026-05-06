import sqlite3

from Config.db import get_connection

MENU_CATEGORIES = ("Nước uống", "Đồ ăn")


def get_categories():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT CategoryID, CategoryName
        FROM Categories
        WHERE CategoryName IN (?, ?)
        ORDER BY CASE CategoryName
            WHEN 'Nước uống' THEN 1
            WHEN 'Đồ ăn' THEN 2
            ELSE 3
        END, CategoryName
        """,
        MENU_CATEGORIES,
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_all_products():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            p.ProductID,
            p.ProductName,
            p.Price,
            p.Status,
            p.ProductImage,
            p.CategoryID,
            COALESCE(c.CategoryName, 'Chưa phân loại') AS CategoryName
        FROM Products p
        LEFT JOIN Categories c ON c.CategoryID = p.CategoryID
        ORDER BY c.CategoryName, p.ProductID DESC
        """
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def create_product(name, price, category_id, status="Còn bán", image_path=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO Products (ProductName, CategoryID, Price, Status, ProductImage)
        VALUES (?, ?, ?, ?, ?)
        """,
        (name, category_id, price, status, image_path),
    )
    conn.commit()
    conn.close()


def update_product(product_id, name, price, category_id, status, image_path=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE Products
        SET ProductName = ?, Price = ?, CategoryID = ?, Status = ?, ProductImage = ?
        WHERE ProductID = ?
        """,
        (name, price, category_id, status, image_path, product_id),
    )
    conn.commit()
    conn.close()


def delete_product(product_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Products WHERE ProductID = ?", (product_id,))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # Product đang được tham chiếu trong OrderDetails nên không thể xóa cứng
        return False
    finally:
        conn.close()
