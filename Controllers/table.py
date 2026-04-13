from Models.table import get_all_tables
from Models.order import get_active_order_by_table

class TableController:

    def load_tables(self):
        return get_all_tables()

    def open_table(self, table_id):
        order = get_active_order_by_table(table_id)

        if order:
            return order   # mở order cũ
        else:
            return None    # tạo order mới