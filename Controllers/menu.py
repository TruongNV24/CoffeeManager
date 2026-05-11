from Models.product import get_active_menu_items


class MenuService:
    """Business logic for filtering menu items away from UI layer."""

    @staticmethod
    def fetch_active_items():
        return get_active_menu_items()

    @staticmethod
    def filter_items(items, current_category="Tất cả", search_keyword=""):
        keyword = (search_keyword or "").strip().lower()
        category = (current_category or "Tất cả").strip().lower()

        filtered = []
        for item in items:
            category_name = (item[6] or "Other").strip()
            name = (item[1] or "").strip()
            item_category_lower = category_name.lower()

            match_category = category == "tất cả" or item_category_lower == category
            if not match_category:
                continue

            if keyword:
                searchable = f"{name} {category_name}".lower()
                if keyword not in searchable:
                    continue

            filtered.append(item)
        return filtered


class MenuController:
    """Controller orchestrates search/category state + menu filtering flow."""

    def __init__(self):
        self.service = MenuService()
        self.current_category = "Tất cả"
        self.search_keyword = ""
        self.all_items = []
        self.filtered_items = []

    def load_menu_items(self):
        self.all_items = self.service.fetch_active_items()
        return self.filter_menu_items()

    def filter_menu_items(self):
        self.filtered_items = self.service.filter_items(
            self.all_items,
            current_category=self.current_category,
            search_keyword=self.search_keyword,
        )
        return self.filtered_items
