from Config.db import get_connection


class ReportService:
    def get_statistics(self, year, month=None):
        conn = get_connection()
        cursor = conn.cursor()

        params = [str(year)]
        date_filter = "strftime('%Y', o.OrderDate) = ?"
        if month:
            date_filter += " AND strftime('%m', o.OrderDate) = ?"
            params.append(f"{int(month):02d}")

        cursor.execute(
            f"""
            SELECT
                COALESCE(SUM(o.TotalAmount), 0),
                COUNT(o.OrderID),
                COALESCE(SUM(od.Quantity), 0)
            FROM Orders o
            LEFT JOIN OrderDetails od ON o.OrderID = od.OrderID
            WHERE {date_filter}
            """,
            params,
        )
        revenue, invoice_count, total_items = cursor.fetchone()

        cursor.execute(
            f"""
            SELECT t.TableName, COUNT(*) AS usage_count
            FROM Orders o
            JOIN Tables t ON o.TableID = t.TableID
            WHERE {date_filter}
            GROUP BY t.TableID, t.TableName
            ORDER BY usage_count DESC
            LIMIT 1
            """,
            params,
        )
        top_table = cursor.fetchone()

        conn.close()
        return {
            "revenue": revenue or 0,
            "invoice_count": invoice_count or 0,
            "total_items": total_items or 0,
            "top_table": top_table[0] if top_table else "—",
        }

    def get_revenue_series(self, year, month=None):
        conn = get_connection()
        cursor = conn.cursor()
        if month:
            cursor.execute(
                """
                SELECT CAST(strftime('%d', OrderDate) AS INTEGER) day, COALESCE(SUM(TotalAmount),0)
                FROM Orders
                WHERE strftime('%Y', OrderDate)=? AND strftime('%m', OrderDate)=?
                GROUP BY day ORDER BY day
                """,
                (str(year), f"{int(month):02d}"),
            )
            rows = cursor.fetchall()
            labels = [str(day) for day, _ in rows]
        else:
            cursor.execute(
                """
                SELECT CAST(strftime('%m', OrderDate) AS INTEGER) month, COALESCE(SUM(TotalAmount),0)
                FROM Orders
                WHERE strftime('%Y', OrderDate)=?
                GROUP BY month ORDER BY month
                """,
                (str(year),),
            )
            rows = cursor.fetchall()
            labels = [f"T{m}" for m, _ in rows]

        conn.close()
        return labels, [value for _, value in rows]

    def get_invoices(self, year, month=None, limit=200):
        conn = get_connection()
        cursor = conn.cursor()
        params = [str(year)]
        date_filter = "strftime('%Y', o.OrderDate) = ?"
        if month:
            date_filter += " AND strftime('%m', o.OrderDate) = ?"
            params.append(f"{int(month):02d}")

        cursor.execute(
            f"""
            SELECT o.OrderID, COALESCE(t.TableName, 'N/A'), o.OrderDate,
                   COALESCE(o.TotalAmount, 0), COALESCE(e.FullName, 'N/A')
            FROM Orders o
            LEFT JOIN Tables t ON o.TableID = t.TableID
            LEFT JOIN Employees e ON o.EmployeeID = e.EmployeeID
            WHERE {date_filter}
            ORDER BY o.OrderDate DESC
            LIMIT ?
            """,
            (*params, limit),
        )
        rows = cursor.fetchall()
        conn.close()
        return rows
