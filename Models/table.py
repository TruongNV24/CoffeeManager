from Config.db import get_connection

def get_all_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Tables")
    tables = cursor.fetchall()

    conn.close()
    return tables