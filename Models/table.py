from Config.db import get_connection

def get_all_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Tables")
    tables = cursor.fetchall()

    conn.close()
    return tables


def create_table(table_name, status="Trống"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Tables (TableName, Status) VALUES (?, ?)",
        (table_name, status),
    )
    conn.commit()
    conn.close()


def update_table(table_id, table_name, status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE Tables SET TableName = ?, Status = ? WHERE TableID = ?",
        (table_name, status, table_id),
    )
    conn.commit()
    conn.close()


def delete_table(table_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Tables WHERE TableID = ?", (table_id,))
    conn.commit()
    conn.close()
