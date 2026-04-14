from Models.order import get_active_order_by_table
from Models.table import (
    create_table,
    delete_table,
    get_all_tables,
    update_table,
    update_table_status,
)


class TableController:
    def load_tables(self):
        return get_all_tables()

    def add_table(self, table_name, status):
        create_table(table_name, status)

    def edit_table(self, table_id, table_name, status):
        update_table(table_id, table_name, status)

    def update_table_status_only(self, table_id, status):
        update_table_status(table_id, status)

    def remove_table(self, table_id):
        delete_table(table_id)

    def open_table(self, table_id):
        order = get_active_order_by_table(table_id)

        if order:
            return order
        return None
