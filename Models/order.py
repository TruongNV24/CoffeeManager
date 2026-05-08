from Config.db import get_connection


def get_active_order_by_table(table_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT OrderID, TableID, EmployeeID, OrderDate, TotalAmount, Status
        FROM Orders
        WHERE TableID=? AND Status='Đang dùng'
        """,
        (table_id,),
    )

    order = cursor.fetchone()
    conn.close()

    return order


def create_or_get_active_order(table_id, employee_id=None):
    existing = get_active_order_by_table(table_id)
    if existing:
        return existing[0]

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Orders (TableID, EmployeeID, Status, TotalAmount) VALUES (?, ?, 'Đang dùng', 0)",
        (table_id, employee_id),
    )
    order_id = cursor.lastrowid
    cursor.execute("UPDATE Tables SET Status='Đang dùng' WHERE TableID = ?", (table_id,))
    conn.commit()
    conn.close()
    return order_id


def add_item_to_order(order_id, product_id, quantity):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT Price FROM Products WHERE ProductID = ?", (product_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise ValueError("Món ăn không tồn tại")

    price = float(row[0])
    subtotal = price * int(quantity)

    cursor.execute(
        """
        INSERT INTO OrderDetails (OrderID, ProductID, Quantity, Price, SubTotal)
        VALUES (?, ?, ?, ?, ?)
        """,
        (order_id, product_id, quantity, price, subtotal),
    )

    cursor.execute(
        "UPDATE Orders SET TotalAmount = COALESCE(TotalAmount, 0) + ? WHERE OrderID = ?",
        (subtotal, order_id),
    )

    conn.commit()
    conn.close()


def get_order_details(order_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT od.OrderDetailID, p.ProductName, od.Quantity, od.Price, od.SubTotal
        FROM OrderDetails od
        JOIN Products p ON p.ProductID = od.ProductID
        WHERE od.OrderID = ?
        ORDER BY od.OrderDetailID DESC
        """,
        (order_id,),
    )
    details = cursor.fetchall()

    cursor.execute("SELECT TotalAmount, Status, TableID FROM Orders WHERE OrderID = ?", (order_id,))
    order = cursor.fetchone()
    conn.close()
    return details, order


def remove_order_detail(order_detail_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT OrderID, SubTotal FROM OrderDetails WHERE OrderDetailID = ?", (order_detail_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False

    order_id, subtotal = row
    cursor.execute("DELETE FROM OrderDetails WHERE OrderDetailID = ?", (order_detail_id,))
    cursor.execute(
        "UPDATE Orders SET TotalAmount = MAX(COALESCE(TotalAmount, 0) - ?, 0) WHERE OrderID = ?",
        (subtotal, order_id),
    )
    conn.commit()
    conn.close()
    return True


def close_order(order_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT TableID FROM Orders WHERE OrderID = ?", (order_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise ValueError("Order không tồn tại")

    table_id = row[0]
    cursor.execute("UPDATE Orders SET Status='Đã thanh toán' WHERE OrderID = ?", (order_id,))
    cursor.execute("UPDATE Tables SET Status='Trống' WHERE TableID = ?", (table_id,))
    conn.commit()
    conn.close()
