from Config.db import get_connection


def get_active_order_by_table(table_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM Orders 
        WHERE TableID=? AND Status='Đang dùng'
    """, (table_id,))

    order = cursor.fetchone()
    conn.close()

    return order
