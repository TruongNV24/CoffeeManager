from Models.order import (
    add_item_to_order,
    close_order,
    create_or_get_active_order,
    get_active_order_by_table,
    get_order_details,
    remove_order_detail,
)
from Models.product import (
    create_product,
    delete_product,
    get_all_categories,
    get_all_products,
    update_product,
)


class OrderController:
    """Controller layer to keep view classes thin and aligned to MVC boundaries."""

    @staticmethod
    def get_categories():
        return get_all_categories()

    @staticmethod
    def get_products():
        return get_all_products()

    @staticmethod
    def create_product(*args, **kwargs):
        return create_product(*args, **kwargs)

    @staticmethod
    def update_product(*args, **kwargs):
        return update_product(*args, **kwargs)

    @staticmethod
    def delete_product(product_id):
        return delete_product(product_id)

    @staticmethod
    def get_active_order_by_table(table_id):
        return get_active_order_by_table(table_id)

    @staticmethod
    def create_or_get_active_order(table_id):
        return create_or_get_active_order(table_id)

    @staticmethod
    def add_item_to_order(order_id, product_id, qty):
        return add_item_to_order(order_id, product_id, qty)

    @staticmethod
    def get_order_details(order_id):
        return get_order_details(order_id)

    @staticmethod
    def remove_order_detail(order_detail_id):
        return remove_order_detail(order_detail_id)

    @staticmethod
    def close_order(order_id):
        return close_order(order_id)
