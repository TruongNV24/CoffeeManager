import sqlite3

from Config.db import get_connection


def get_all_categories():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT CategoryID, CategoryName
        FROM Categories
        ORDER BY CategoryName COLLATE NOCASE
        """
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
            c.CategoryName
        FROM Products p
        LEFT JOIN Categories c ON c.CategoryID = p.CategoryID
        ORDER BY p.ProductID DESC
        """
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def create_product(name, price, status="Còn bán", image_path=None, category_id=None):
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


def update_product(product_id, name, price, status, image_path=None, category_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE Products
        SET ProductName = ?, CategoryID = ?, Price = ?, Status = ?, ProductImage = ?
        WHERE ProductID = ?
        """,
        (name, category_id, price, status, image_path, product_id),
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
