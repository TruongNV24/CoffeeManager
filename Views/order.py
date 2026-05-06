import os
import shutil
import tkinter as tk
import uuid
from tkinter import filedialog, messagebox, ttk

from Config.db import get_connection
from Config.image_config import CARD_IMAGE_SIZE, PREVIEW_IMAGE_SIZE
from Models.order import (
    add_item_to_order,
    close_order,
    create_or_get_active_order,
    get_active_order_by_table,
    get_order_details,
)
from Models.product import (
    create_product,
    delete_product,
    get_all_products,
    get_categories,
    update_product,
)
from Utils.image_handler import ImageHandler
from Views.theme import COLORS, FONT_FAMILY, button, entry


class OrderView:
    def __init__(self, parent, role):
        self.parent = parent
        self.role = role
        self.selected_product_id = None
        self.current_order_id = None
        self.current_image_preview = None
        self.product_cards = {}
        self.product_image_labels = {}
        self.categories = []
        self.category_map = {}
        self.products = []
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.image_handler = ImageHandler(self.project_root)

        self.frame = tk.Frame(parent, bg=COLORS["app_bg"])
        self.frame.pack(fill="both", expand=True)

        self._build_ui()
        self.load_categories()
        self.load_tables()
        self.load_products()

    def _build_ui(self):
        header = tk.Frame(self.frame, bg=COLORS["app_bg"])
        header.pack(fill="x", padx=24, pady=(20, 10))

        title_box = tk.Frame(header, bg=COLORS["app_bg"])
        title_box.pack(side="left", fill="x", expand=True)
        tk.Label(
            title_box,
            text="Gọi món & quản lý menu",
            bg=COLORS["app_bg"],
            fg=COLORS["text"],
            font=(FONT_FAMILY, 20, "bold"),
        ).pack(anchor="w")
        tk.Label(
            title_box,
            text="Chọn bàn, thêm món vào order và cập nhật danh mục menu trong cùng một màn hình.",
            bg=COLORS["app_bg"],
            fg=COLORS["muted"],
            font=(FONT_FAMILY, 10),
        ).pack(anchor="w", pady=(3, 0))

        order_controls = tk.Frame(
            header,
            bg=COLORS["surface"],
            padx=14,
            pady=12,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
        )
        order_controls.pack(side="right", fill="x")
        self._field_label(order_controls, "Bàn", 0, 0)
        self.table_var = tk.StringVar()
        self.table_var.trace_add("write", self._on_table_change)
        self.table_menu = tk.OptionMenu(order_controls, self.table_var, "")
        self._style_option_menu(self.table_menu, width=18)
        self.table_menu.grid(row=1, column=0, sticky="ew", padx=(0, 10), ipady=2)

        self._field_label(order_controls, "Số lượng", 0, 1)
        self.qty_var = tk.StringVar(value="1")
        entry(order_controls, textvariable=self.qty_var, width=7, justify="center").grid(
            row=1, column=1, sticky="ew", padx=(0, 10), ipady=7
        )

        button(order_controls, text="+ Thêm order", variant="success", command=self.add_to_order).grid(row=1, column=2, padx=(0, 6))
        button(order_controls, text="Xem order", variant="ghost", command=self.show_current_order).grid(row=1, column=3, padx=(0, 6))
        button(order_controls, text="Thanh toán", variant="warning", command=self.export_invoice).grid(row=1, column=4)

        if self.role == "Admin":
            self._build_product_form()
        else:
            self.product_name_var = tk.StringVar(value="(Chỉ admin được CRUD món)")
            self.product_price_var = tk.StringVar()
            self.product_status_var = tk.StringVar(value="Còn bán")
            self.product_image_var = tk.StringVar()
            self.product_category_var = tk.StringVar()
            self.image_preview_label = tk.Label(self.frame)

        body = tk.Frame(self.frame, bg=COLORS["app_bg"])
        body.pack(fill="both", expand=True, padx=24, pady=(0, 22))

        left = tk.Frame(body, bg=COLORS["surface"], highlightthickness=1, highlightbackground=COLORS["border"])
        left.pack(side="left", fill="both", expand=True, padx=(0, 14))

        list_header = tk.Frame(left, bg=COLORS["surface"], padx=14, pady=12)
        list_header.pack(fill="x")
        tk.Label(
            list_header,
            text="Danh sách món",
            bg=COLORS["surface"],
            fg=COLORS["text"],
            font=(FONT_FAMILY, 14, "bold"),
        ).pack(side="left")
        tk.Label(
            list_header,
            text="Chọn một món để gọi hoặc sửa thông tin",
            bg=COLORS["surface"],
            fg=COLORS["muted"],
            font=(FONT_FAMILY, 10),
        ).pack(side="left", padx=(12, 0))

        self.category_filter_var = tk.StringVar(value="Tất cả")
        self.category_filter = ttk.Combobox(list_header, textvariable=self.category_filter_var, width=16, state="readonly")
        self.category_filter.pack(side="right")
        self.category_filter.bind("<<ComboboxSelected>>", lambda _e: self.render_product_cards())
        tk.Label(list_header, text="Lọc:", bg=COLORS["surface"], fg=COLORS["muted"]).pack(side="right", padx=(0, 6))

        grid_wrap = tk.Frame(left, bg=COLORS["surface"], padx=12, pady=(0, 12))
        grid_wrap.pack(fill="both", expand=True)

        self.product_canvas = tk.Canvas(grid_wrap, bg=COLORS["surface"], highlightthickness=0)
        self.product_scrollbar = tk.Scrollbar(grid_wrap, orient="vertical", command=self.product_canvas.yview)
        self.product_canvas.configure(yscrollcommand=self.product_scrollbar.set)
        self.product_canvas.pack(side="left", fill="both", expand=True)
        self.product_scrollbar.pack(side="right", fill="y")

        self.product_grid = tk.Frame(self.product_canvas, bg=COLORS["surface"])
        self.product_canvas_window = self.product_canvas.create_window((0, 0), window=self.product_grid, anchor="nw")
        self.product_grid.bind("<Configure>", lambda _e: self.product_canvas.configure(scrollregion=self.product_canvas.bbox("all")))
        self.product_canvas.bind("<Configure>", self._on_product_canvas_resize)

        right = tk.Frame(body, bg="#fff7ed", highlightthickness=1, highlightbackground=COLORS["border"], width=360)
        right.pack(side="right", fill="both")
        right.pack_propagate(False)

        order_header = tk.Frame(right, bg="#fff7ed", padx=14, pady=12)
        order_header.pack(fill="x")
        tk.Label(order_header, text="Chi tiết order", bg="#fff7ed", fg=COLORS["text"], font=(FONT_FAMILY, 14, "bold")).pack(anchor="w")
        tk.Label(order_header, text="Hóa đơn tạm thời của bàn đang chọn", bg="#fff7ed", fg=COLORS["muted"]).pack(anchor="w")
        self.order_text = tk.Text(right, height=26, bg="#fff7ed", fg=COLORS["text"], relief="flat", font=("Consolas", 10))
        self.order_text.pack(fill="both", expand=True, padx=14, pady=(0, 14))

    def _build_product_form(self):
        self.product_form = tk.Frame(
            self.frame,
            bg=COLORS["surface"],
            padx=18,
            pady=16,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
        )
        self.product_form.pack(fill="x", padx=24, pady=(0, 14))

        form_title = tk.Frame(self.product_form, bg=COLORS["surface"])
        form_title.grid(row=0, column=0, columnspan=6, sticky="ew", pady=(0, 12))
        tk.Label(
            form_title,
            text="CRUD món",
            bg=COLORS["surface"],
            fg=COLORS["text"],
            font=(FONT_FAMILY, 14, "bold"),
        ).pack(side="left")
        tk.Label(
            form_title,
            text="Nhập thông tin theo từng cụm để layout thoáng hơn, không bị vướng nút thao tác.",
            bg=COLORS["surface"],
            fg=COLORS["muted"],
            font=(FONT_FAMILY, 10),
        ).pack(side="left", padx=(12, 0))

        self.product_name_var = tk.StringVar()
        self.product_price_var = tk.StringVar()
        self.product_category_var = tk.StringVar()
        self.product_status_var = tk.StringVar(value="Còn bán")
        self.product_image_var = tk.StringVar()

        self._field_label(self.product_form, "Tên món", 1, 0)
        entry(self.product_form, textvariable=self.product_name_var, width=28, font=(FONT_FAMILY, 11)).grid(row=2, column=0, sticky="ew", padx=(0, 12), ipady=7)

        self._field_label(self.product_form, "Giá", 1, 1)
        entry(self.product_form, textvariable=self.product_price_var, width=14, justify="right", font=(FONT_FAMILY, 11)).grid(row=2, column=1, sticky="ew", padx=(0, 12), ipady=7)

        self._field_label(self.product_form, "Danh mục", 1, 2)
        self.product_category_combo = ttk.Combobox(self.product_form, textvariable=self.product_category_var, width=16, state="readonly")
        self.product_category_combo.grid(row=2, column=2, sticky="ew", padx=(0, 12), ipady=4)

        self._field_label(self.product_form, "Trạng thái", 1, 3)
        self.product_status_menu = tk.OptionMenu(self.product_form, self.product_status_var, "Còn bán", "Hết món")
        self._style_option_menu(self.product_status_menu, width=12)
        self.product_status_menu.grid(row=2, column=3, sticky="ew", padx=(0, 12), ipady=2)

        self._field_label(self.product_form, "Ảnh món", 3, 0)
        entry(self.product_form, textvariable=self.product_image_var, width=42).grid(row=4, column=0, columnspan=2, sticky="ew", padx=(0, 12), ipady=7, pady=(8, 0))
        button(self.product_form, text="Chọn ảnh", variant="ghost", command=self.pick_product_image).grid(row=4, column=2, sticky="ew", padx=(0, 12), pady=(8, 0))

        self.image_preview_label = tk.Label(self.product_form, text="(Chưa có ảnh)", bg=COLORS["surface_alt"], fg=COLORS["muted"], width=16, height=4)
        self.image_preview_label.grid(row=1, column=4, rowspan=4, sticky="nsew", padx=(6, 14))

        actions = tk.Frame(self.product_form, bg=COLORS["surface"])
        actions.grid(row=1, column=5, rowspan=4, sticky="nsew")
        self.btn_add = button(actions, text="+ Thêm món", variant="success", command=self.add_product)
        self.btn_add.pack(fill="x", pady=(0, 8))
        self.btn_update = button(actions, text="Lưu sửa", variant="info", command=self.update_product_info)
        self.btn_update.pack(fill="x", pady=(0, 8))
        self.btn_delete = button(actions, text="Xóa món", variant="danger", command=self.delete_product_info)
        self.btn_delete.pack(fill="x")

        for column in (0, 1, 2, 3):
            self.product_form.grid_columnconfigure(column, weight=1)

    def _field_label(self, parent, text, row, column):
        tk.Label(parent, text=text, bg=parent.cget("bg"), fg=COLORS["muted"], font=(FONT_FAMILY, 10, "bold")).grid(
            row=row, column=column, sticky="w", padx=(0, 8), pady=(0, 4)
        )

    def _style_option_menu(self, menu, width=12):
        menu.config(width=width, bg=COLORS["white"], fg=COLORS["text"], activebackground=COLORS["surface_alt"], relief="flat", highlightthickness=1, highlightbackground=COLORS["border"])
        menu["menu"].config(bg=COLORS["white"], fg=COLORS["text"])

    def load_categories(self):
        self.categories = get_categories()
        self.category_map = {name: category_id for category_id, name in self.categories}
        category_names = list(self.category_map.keys())
        if hasattr(self, "product_category_combo"):
            self.product_category_combo["values"] = category_names
            if category_names and not self.product_category_var.get():
                self.product_category_var.set(category_names[0])
        self.category_filter["values"] = ["Tất cả", *category_names]
        if self.category_filter_var.get() not in self.category_filter["values"]:
            self.category_filter_var.set("Tất cả")

    def load_tables(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT TableID, TableName, Status FROM Tables ORDER BY TableID")
        rows = cursor.fetchall()
        conn.close()

        menu = self.table_menu["menu"]
        menu.delete(0, "end")
        options = []
        for table_id, name, status in rows:
            label = f"{table_id} - {name} ({status})"
            options.append(label)
            menu.add_command(label=label, command=lambda value=label: self.table_var.set(value))

        self.table_var.set(options[0] if options else "")
        self._sync_current_order_with_selected_table()

    def load_products(self):
        self.products = get_all_products()
        self.image_handler.clear_group("cards")
        self.render_product_cards()

    def on_select_product(self, _event=None):
        if self.selected_product_id is None:
            return
        product = next((p for p in self.products if p[0] == self.selected_product_id), None)
        if not product:
            return
        self.product_name_var.set(product[1])
        self.product_price_var.set(str(product[2]))
        self.product_status_var.set(product[3])
        self.product_image_var.set(product[4] or "")
        self.product_category_var.set(product[6])
        self.refresh_image_preview(product[4])
        self._refresh_selected_card()

    def _on_product_canvas_resize(self, event):
        self.product_canvas.itemconfig(self.product_canvas_window, width=event.width)

    def render_product_cards(self):
        for widget in self.product_grid.winfo_children():
            widget.destroy()

        self.product_cards = {}
        self.product_image_labels = {}
        card_width = 156
        columns = 4
        selected_category = self.category_filter_var.get()
        visible_products = [
            product for product in self.products if selected_category == "Tất cả" or product[6] == selected_category
        ]

        if not visible_products:
            tk.Label(
                self.product_grid,
                text="Chưa có món trong danh mục này.",
                bg=COLORS["surface"],
                fg=COLORS["muted"],
                font=(FONT_FAMILY, 11),
            ).grid(row=0, column=0, sticky="w", padx=8, pady=12)

        for idx, product in enumerate(visible_products):
            row = idx // columns
            column = idx % columns
            card = tk.Frame(
                self.product_grid,
                bg=COLORS["white"],
                bd=1,
                relief="solid",
                width=card_width,
                height=214,
                cursor="hand2",
                padx=9,
                pady=9,
            )
            card.grid(row=row, column=column, padx=7, pady=7, sticky="n")
            card.grid_propagate(False)

            image = self.image_handler.get_image(product[4], CARD_IMAGE_SIZE, cache_group="cards")
            image_box = tk.Frame(card, bg=COLORS["white"], width=CARD_IMAGE_SIZE[0], height=CARD_IMAGE_SIZE[1])
            image_box.pack(pady=(0, 8))
            image_box.pack_propagate(False)

            image_label = tk.Label(image_box, image=image, bg=COLORS["white"])
            image_label.image = image
            image_label.place(relx=0.5, rely=0.5, anchor="center")

            category_label = tk.Label(
                card,
                text=product[6],
                bg="#fef3c7" if product[6] == "Đồ ăn" else "#dbeafe",
                fg="#92400e" if product[6] == "Đồ ăn" else "#1d4ed8",
                font=(FONT_FAMILY, 8, "bold"),
            )
            category_label.pack(fill="x", pady=(0, 5))

            name_label = tk.Label(
                card,
                text=product[1],
                bg=COLORS["white"],
                fg=COLORS["text"],
                font=(FONT_FAMILY, 10, "bold"),
                wraplength=130,
                justify="center",
                height=2,
            )
            name_label.pack(fill="x")

            price_label = tk.Label(
                card,
                text=f"{product[2]:,.0f}đ",
                bg=COLORS["white"],
                fg=COLORS["primary_dark"],
                font=(FONT_FAMILY, 10, "bold"),
            )
            price_label.pack(pady=(4, 0))

            status_text = "HẾT MÓN" if product[3] == "Hết món" else "CÒN BÁN"
            status_bg = "#fee2e2" if product[3] == "Hết món" else "#dcfce7"
            status_fg = "#c0392b" if product[3] == "Hết món" else COLORS["success"]
            sold_out = tk.Label(card, text=status_text, bg=status_bg, fg=status_fg, font=(FONT_FAMILY, 8, "bold"), height=1)
            sold_out.pack(pady=(7, 0), fill="x")

            for widget in (card, image_label, category_label, name_label, price_label, sold_out):
                self._bind_card_click(widget, product[0])
            self.product_cards[product[0]] = card
            self.product_image_labels[product[0]] = image_label

        self._refresh_selected_card()
        self.product_canvas.configure(scrollregion=self.product_canvas.bbox("all"))

    def _bind_card_click(self, widget, product_id):
        widget.bind("<Button-1>", lambda _e, pid=product_id: self.select_product_by_id(pid))

    def select_product_by_id(self, product_id):
        self.selected_product_id = product_id
        self.on_select_product()

    def _refresh_selected_card(self):
        for pid, card in self.product_cards.items():
            if pid == self.selected_product_id:
                card.configure(bg="#fff0d9", bd=2, relief="solid")
            else:
                card.configure(bg=COLORS["white"], bd=1, relief="solid")

    def _selected_table_id(self):
        raw = self.table_var.get().strip()
        if not raw:
            return None
        return int(raw.split("-")[0].strip())

    def _on_table_change(self, *_args):
        self._sync_current_order_with_selected_table()

    def _sync_current_order_with_selected_table(self):
        table_id = self._selected_table_id()
        if not table_id:
            self.current_order_id = None
            return

        active_order = get_active_order_by_table(table_id)
        self.current_order_id = active_order[0] if active_order else None

    def _selected_category_id(self):
        category_name = self.product_category_var.get().strip()
        return self.category_map.get(category_name)

    def _validate_product_form(self):
        name = self.product_name_var.get().strip()
        status = self.product_status_var.get()
        category_id = self._selected_category_id()
        try:
            price = float(self.product_price_var.get().strip())
        except ValueError:
            messagebox.showwarning("Sai dữ liệu", "Giá món không hợp lệ")
            return None
        if not name:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập tên món")
            return None
        if not category_id:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng chọn danh mục món")
            return None
        return name, price, category_id, status, self.product_image_var.get().strip() or None

    def add_product(self):
        if self.role != "Admin":
            return
        product_data = self._validate_product_form()
        if not product_data:
            return
        name, price, category_id, status, image_path = product_data
        create_product(name, price, category_id, status, image_path)
        self.load_products()

    def update_product_info(self):
        if self.role != "Admin" or not self.selected_product_id:
            return
        product_data = self._validate_product_form()
        if not product_data:
            return
        name, price, category_id, status, image_path = product_data
        update_product(
            self.selected_product_id,
            name,
            price,
            category_id,
            status,
            image_path,
        )
        self.load_products()

    def delete_product_info(self):
        if self.role != "Admin" or not self.selected_product_id:
            return
        if not messagebox.askyesno("Xác nhận", "Xóa món đã chọn?"):
            return
        deleted = delete_product(self.selected_product_id)
        if not deleted:
            messagebox.showerror(
                "Không thể xóa",
                "Món này đã xuất hiện trong order nên không thể xóa. Hãy chuyển trạng thái sang Hết món.",
            )
            return
        self.selected_product_id = None
        self.load_products()

    def add_to_order(self):
        if not self.selected_product_id:
            messagebox.showwarning("Chưa chọn món", "Vui lòng chọn món cần gọi")
            return

        table_id = self._selected_table_id()
        if not table_id:
            messagebox.showwarning("Chưa có bàn", "Vui lòng tạo bàn trước khi gọi món")
            return

        try:
            qty = int(self.qty_var.get().strip())
            if qty <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Sai dữ liệu", "Số lượng phải là số nguyên dương")
            return

        order_id = create_or_get_active_order(table_id)
        add_item_to_order(order_id, self.selected_product_id, qty)
        self.current_order_id = order_id
        self.load_tables()
        self.show_current_order()

    def show_current_order(self):
        self._sync_current_order_with_selected_table()
        order_id = self.current_order_id
        if not order_id:
            self.order_text.delete("1.0", tk.END)
            self.order_text.insert(tk.END, "Chưa có order đang chọn.\n")
            return

        details, order_info = get_order_details(order_id)
        self.order_text.delete("1.0", tk.END)
        if not details:
            self.order_text.insert(tk.END, "Order chưa có món.\n")
            return

        total = order_info[0] or 0
        status = order_info[1]
        table_id = order_info[2]
        self.order_text.insert(tk.END, f"Order #{order_id} | Bàn {table_id} | {status}\n")
        self.order_text.insert(tk.END, "-" * 45 + "\n")
        for _, name, qty, price, subtotal in details:
            self.order_text.insert(tk.END, f"{name} x{qty}  {price:,.0f}đ  = {subtotal:,.0f}đ\n")
        self.order_text.insert(tk.END, "-" * 45 + "\n")
        self.order_text.insert(tk.END, f"TỔNG: {total:,.0f}đ\n")

    def export_invoice(self):
        if not self.current_order_id:
            messagebox.showwarning("Chưa có order", "Vui lòng tạo order trước")
            return

        details, order_info = get_order_details(self.current_order_id)
        if not details:
            messagebox.showwarning("Order rỗng", "Order chưa có món để xuất hóa đơn")
            return

        total = order_info[0] or 0
        table_id = order_info[2]
        lines = [
            f"HÓA ĐƠN ORDER #{self.current_order_id}",
            f"Bàn: {table_id}",
            "=" * 40,
        ]
        for _, name, qty, price, subtotal in details:
            lines.append(f"{name} x{qty} | {price:,.0f}đ | {subtotal:,.0f}đ")
        lines.append("=" * 40)
        lines.append(f"Tổng tiền: {total:,.0f}đ")

        os.makedirs("invoices", exist_ok=True)
        file_path = os.path.join("invoices", f"invoice_order_{self.current_order_id}.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        paid_order_id = self.current_order_id
        close_order(paid_order_id)
        messagebox.showinfo("Xuất hóa đơn", f"Đã xuất hóa đơn: {file_path}\nOrder đã thanh toán.")
        self.current_order_id = None
        self.load_tables()
        self.order_text.delete("1.0", tk.END)
        self.order_text.insert(tk.END, f"Đã thanh toán order #{paid_order_id}.\n")

    def pick_product_image(self):
        file_path = filedialog.askopenfilename(
            title="Chọn ảnh món",
            filetypes=[("Image files", "*.png *.gif *.ppm *.pgm *.jpg *.jpeg"), ("All files", "*.*")],
        )
        if not file_path:
            return

        os.makedirs(os.path.join(self.project_root, "uploads"), exist_ok=True)
        ext = os.path.splitext(file_path)[1].lower()
        new_name = f"{uuid.uuid4().hex}{ext}"
        new_path = os.path.join("uploads", new_name)
        new_abs_path = os.path.join(self.project_root, new_path)
        shutil.copy2(file_path, new_abs_path)
        self.product_image_var.set(new_path)
        self.refresh_image_preview(new_path)

    def refresh_image_preview(self, image_path):
        resolved_path = self.image_handler.resolve_path(image_path)
        if not resolved_path:
            self.current_image_preview = None
            self.image_preview_label.configure(image="", text="(Chưa có ảnh)")
            return

        self.current_image_preview = self.image_handler.get_image(resolved_path, PREVIEW_IMAGE_SIZE, cache_group="preview")
        self.image_preview_label.configure(image=self.current_image_preview, text="")
        self.image_preview_label.image = self.current_image_preview
