from Config.db import get_connection


def get_all_products():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT ProductID, ProductName, Price, Status, ProductImage
        FROM Products
        ORDER BY ProductID DESC
        """
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def create_product(name, price, status="Còn bán", image_path=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Products (ProductName, Price, Status, ProductImage) VALUES (?, ?, ?, ?)",
        (name, price, status, image_path),
    )
    conn.commit()
    conn.close()


def update_product(product_id, name, price, status, image_path=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE Products
        SET ProductName = ?, Price = ?, Status = ?, ProductImage = ?
        WHERE ProductID = ?
        """,
        (name, price, status, image_path, product_id),
    )
    conn.commit()
    conn.close()


def delete_product(product_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Products WHERE ProductID = ?", (product_id,))
    conn.commit()
    conn.close()
