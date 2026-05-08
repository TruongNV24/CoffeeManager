import os
import shutil
import tkinter as tk
import uuid
from tkinter import filedialog, messagebox

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
    get_all_categories,
    get_all_products,
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
        self.category_placeholder = "Chưa chọn loại"
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.image_handler = ImageHandler(self.project_root)

        self.frame = tk.Frame(parent, bg=COLORS["app_bg"])
        self.frame.pack(fill="both", expand=True)

        self._build_ui()
        self.load_categories()
        self.load_tables()
        self.load_products()

    def _build_ui(self):
        top = tk.Frame(self.frame, bg=COLORS["surface"], padx=16, pady=14, highlightthickness=1, highlightbackground=COLORS["border"])
        top.pack(fill="x", padx=22, pady=(20, 12))

        tk.Label(top, text="Bàn:", bg=COLORS["surface"], fg=COLORS["text"], font=(FONT_FAMILY, 11, "bold")).pack(side="left")
        self.table_var = tk.StringVar()
        self.table_var.trace_add("write", self._on_table_change)
        self.table_menu = tk.OptionMenu(top, self.table_var, "")
        self.table_menu.config(width=18)
        self.table_menu.pack(side="left", padx=6)

        tk.Label(top, text="Số lượng:", bg=COLORS["surface"], fg=COLORS["text"], font=(FONT_FAMILY, 11, "bold")).pack(side="left", padx=(8, 0))
        self.qty_var = tk.StringVar(value="1")
        entry(top, textvariable=self.qty_var, width=5).pack(side="left", padx=6, ipady=5)

        button(top, text="Thêm vào order", variant="success", command=self.add_to_order).pack(side="left", padx=8)
        button(top, text="Xem order", variant="ghost", command=self.show_current_order).pack(side="left", padx=4)
        button(top, text="Xuất hóa đơn & Thanh toán", variant="warning", command=self.export_invoice).pack(side="left", padx=4)

        body = tk.Frame(self.frame, bg=COLORS["app_bg"])
        body.pack(fill="both", expand=True, padx=22, pady=(0, 22))

        left = tk.Frame(body, bg=COLORS["surface"], highlightthickness=1, highlightbackground=COLORS["border"])
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))

        product_header = tk.Frame(left, bg=COLORS["surface"])
        product_header.pack(fill="x", padx=10, pady=8)
        tk.Label(
            product_header,
            text="Danh sách món",
            bg=COLORS["surface"],
            fg=COLORS["text"],
            font=(FONT_FAMILY, 14, "bold"),
        ).pack(side="left")
        self.product_form_visible = False
        self.toggle_product_form_button = button(
            product_header,
            text="Hiện CRUD món",
            variant="ghost",
            command=self.toggle_product_form,
        )
        if self.role == "Admin":
            self.toggle_product_form_button.pack(side="right")

        grid_wrap = tk.Frame(left, bg=COLORS["surface"])
        grid_wrap.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.product_canvas = tk.Canvas(grid_wrap, bg=COLORS["surface"], highlightthickness=0)
        self.product_scrollbar = tk.Scrollbar(grid_wrap, orient="vertical", command=self.product_canvas.yview)
        self.product_canvas.configure(yscrollcommand=self.product_scrollbar.set)
        self.product_canvas.pack(side="left", fill="both", expand=True)
        self.product_scrollbar.pack(side="right", fill="y")

        self.product_grid = tk.Frame(self.product_canvas, bg=COLORS["surface"])
        self.product_canvas_window = self.product_canvas.create_window((0, 0), window=self.product_grid, anchor="nw")
        self.product_grid.bind("<Configure>", lambda _e: self.product_canvas.configure(scrollregion=self.product_canvas.bbox("all")))
        self.product_canvas.bind("<Configure>", self._on_product_canvas_resize)

        self.product_form = tk.Frame(left, bg=COLORS["surface_alt"], padx=10, pady=10)

        tk.Label(self.product_form, text="Tên món", bg=COLORS["surface_alt"]).grid(row=0, column=0, sticky="w")
        tk.Label(self.product_form, text="Giá", bg=COLORS["surface_alt"]).grid(row=0, column=1, sticky="w")
        tk.Label(self.product_form, text="Loại sản phẩm", bg=COLORS["surface_alt"]).grid(row=0, column=2, sticky="w")
        tk.Label(self.product_form, text="Trạng thái", bg=COLORS["surface_alt"]).grid(row=0, column=3, sticky="w")
        tk.Label(self.product_form, text="Ảnh", bg=COLORS["surface_alt"]).grid(row=2, column=0, sticky="w", pady=(4, 0))
        self.product_name_var = tk.StringVar()
        self.product_price_var = tk.StringVar()
        self.product_category_var = tk.StringVar(value=self.category_placeholder)
        self.product_status_var = tk.StringVar(value="Còn bán")
        self.product_image_var = tk.StringVar()
        entry(self.product_form, textvariable=self.product_name_var, width=20).grid(row=1, column=0, padx=(0, 8), pady=4)
        entry(self.product_form, textvariable=self.product_price_var, width=10).grid(row=1, column=1, padx=(0, 8), pady=4)
        self.product_category_menu = tk.OptionMenu(self.product_form, self.product_category_var, self.category_placeholder)
        self.product_category_menu.config(width=16)
        self.product_category_menu.grid(row=1, column=2, padx=(0, 8), pady=4, sticky="we")
        tk.OptionMenu(self.product_form, self.product_status_var, "Còn bán", "Hết món").grid(row=1, column=3, padx=(0, 8), pady=4)
        entry(self.product_form, textvariable=self.product_image_var, width=34).grid(row=3, column=0, columnspan=3, sticky="we")
        button(self.product_form, text="Chọn ảnh", variant="ghost", command=self.pick_product_image).grid(row=3, column=3, padx=(0, 8))

        actions = tk.Frame(self.product_form, bg=COLORS["surface_alt"])
        actions.grid(row=1, column=4)
        self.btn_add = button(actions, text="Thêm", variant="success", command=self.add_product)
        self.btn_add.pack(side="left", padx=2)
        self.btn_update = button(actions, text="Sửa", variant="info", command=self.update_product_info)
        self.btn_update.pack(side="left", padx=2)
        self.btn_delete = button(actions, text="Xóa", variant="danger", command=self.delete_product_info)
        self.btn_delete.pack(side="left", padx=2)
        self.image_preview_label = tk.Label(self.product_form, text="(Chưa có ảnh)", bg=COLORS["surface_alt"], fg="#666")
        self.image_preview_label.grid(row=3, column=4, padx=8)

        right = tk.Frame(body, bg="#fff7ed", highlightthickness=1, highlightbackground=COLORS["border"], width=360)
        right.pack(side="right", fill="both")
        right.pack_propagate(False)

        tk.Label(right, text="Chi tiết order", bg="#fff7ed", fg=COLORS["text"], font=(FONT_FAMILY, 14, "bold")).pack(anchor="w", padx=10, pady=8)
        self.order_text = tk.Text(right, height=26, bg="#fff7ed", fg=COLORS["text"], relief="flat", font=("Consolas", 10))
        self.order_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        if self.role != "Admin":
            self.btn_add.config(state="disabled")
            self.btn_update.config(state="disabled")
            self.btn_delete.config(state="disabled")
            self.product_name_var.set("(Chỉ admin được CRUD món)")

    def toggle_product_form(self):
        self.set_product_form_visible(not self.product_form_visible)

    def set_product_form_visible(self, visible):
        self.product_form_visible = visible
        if visible:
            self.product_form.pack(fill="x", padx=10, pady=(0, 10))
            self.toggle_product_form_button.config(text="Ẩn CRUD món")
        else:
            self.product_form.pack_forget()
            self.toggle_product_form_button.config(text="Hiện CRUD món")

    def load_categories(self):
        self.categories = get_all_categories()
        menu = self.product_category_menu["menu"]
        menu.delete(0, "end")
        menu.add_command(
            label=self.category_placeholder,
            command=lambda: self.product_category_var.set(self.category_placeholder),
        )

        for category_id, category_name in self.categories:
            label = self._category_label(category_id, category_name)
            menu.add_command(label=label, command=lambda value=label: self.product_category_var.set(value))

        self.product_category_var.set(self.category_placeholder)

    def _category_label(self, category_id, category_name):
        return f"{category_id} - {category_name}"

    def _selected_category_id(self):
        raw = self.product_category_var.get().strip()
        if not raw or raw == self.category_placeholder:
            return None
        return int(raw.split("-")[0].strip())

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
        category_id = product[5] if len(product) > 5 else None
        category_name = product[6] if len(product) > 6 else None
        self.product_category_var.set(
            self._category_label(category_id, category_name)
            if category_id and category_name
            else self.category_placeholder
        )
        self.product_image_var.set(product[4] or "")
        self.refresh_image_preview(product[4])
        self._refresh_selected_card()

    def _on_product_canvas_resize(self, event):
        self.product_canvas.itemconfig(self.product_canvas_window, width=event.width)

    def render_product_cards(self):
        for widget in self.product_grid.winfo_children():
            widget.destroy()

        self.product_cards = {}
        self.product_image_labels = {}
        card_width = 140
        columns = 4

        for idx, product in enumerate(self.products):
            row = idx // columns
            column = idx % columns
            card = tk.Frame(
                self.product_grid,
                bg=COLORS["white"],
                bd=0,
                relief="flat",
                highlightthickness=2,
                highlightbackground=COLORS["border"],
                highlightcolor=COLORS["border"],
                width=card_width,
                height=200,
                cursor="hand2",
                padx=8,
                pady=8,
            )
            card.grid(row=row, column=column, padx=6, pady=6, sticky="n")
            card.grid_propagate(False)

            image = self.image_handler.get_image(product[4], CARD_IMAGE_SIZE, cache_group="cards")
            image_box = tk.Frame(card, bg=COLORS["white"], width=CARD_IMAGE_SIZE[0], height=CARD_IMAGE_SIZE[1])
            image_box.pack(pady=(0, 8))
            image_box.pack_propagate(False)

            image_label = tk.Label(image_box, image=image, bg=COLORS["white"])
            image_label.image = image
            image_label.place(relx=0.5, rely=0.5, anchor="center")

            name_label = tk.Label(
                card,
                text=product[1],
                bg=COLORS["white"],
                font=(FONT_FAMILY, 10, "bold"),
                wraplength=116,
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

            category_label = tk.Label(
                card,
                text=product[6] or "Chưa phân loại",
                bg=COLORS["white"],
                fg=COLORS["muted"],
                font=(FONT_FAMILY, 9),
                wraplength=116,
                justify="center",
            )
            category_label.pack(pady=(2, 0), fill="x")

            status_text = "HẾT MÓN" if product[3] == "Hết món" else ""
            status_bg = "#fee2e2" if product[3] == "Hết món" else COLORS["white"]
            status_fg = "#c0392b" if product[3] == "Hết món" else "white"
            sold_out = tk.Label(card, text=status_text, bg=status_bg, fg=status_fg, font=(FONT_FAMILY, 9, "bold"), height=1)
            sold_out.pack(pady=(8, 0), fill="x")

            self._bind_card_click(card, product[0])
            self._bind_card_click(image_label, product[0])
            self._bind_card_click(name_label, product[0])
            self._bind_card_click(price_label, product[0])
            self._bind_card_click(category_label, product[0])
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
                card.configure(bg="#fff0d9", highlightbackground=COLORS["accent"], highlightcolor=COLORS["accent"])
            else:
                card.configure(bg=COLORS["white"], highlightbackground=COLORS["border"], highlightcolor=COLORS["border"])


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

    def add_product(self):
        if self.role != "Admin":
            return
        name = self.product_name_var.get().strip()
        status = self.product_status_var.get()
        category_id = self._selected_category_id()
        if not category_id:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng chọn loại sản phẩm")
            return
        try:
            price = float(self.product_price_var.get().strip())
        except ValueError:
            messagebox.showwarning("Sai dữ liệu", "Giá món không hợp lệ")
            return
        if not name:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập tên món")
            return
        create_product(
            name,
            price,
            status,
            self.product_image_var.get().strip() or None,
            category_id,
        )
        self.load_products()

    def update_product_info(self):
        if self.role != "Admin" or not self.selected_product_id:
            return
        name = self.product_name_var.get().strip()
        status = self.product_status_var.get()
        category_id = self._selected_category_id()
        if not category_id:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng chọn loại sản phẩm")
            return
        try:
            price = float(self.product_price_var.get().strip())
        except ValueError:
            messagebox.showwarning("Sai dữ liệu", "Giá món không hợp lệ")
            return
        update_product(
            self.selected_product_id,
            name,
            price,
            status,
            self.product_image_var.get().strip() or None,
            category_id,
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
