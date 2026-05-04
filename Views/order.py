import os
import shutil
import tkinter as tk
import uuid
from tkinter import filedialog, messagebox

from Config.db import get_connection
from Models.order import (
    add_item_to_order,
    close_order,
    create_or_get_active_order,
    get_order_details,
)
from Models.product import (
    create_product,
    delete_product,
    get_all_products,
    update_product,
)


class OrderView:
    def __init__(self, parent, role):
        self.parent = parent
        self.role = role
        self.selected_product_id = None
        self.current_order_id = None
        self.current_image_preview = None
        self.card_image_cache = {}
        self.product_cards = {}
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        self.frame = tk.Frame(parent, bg="white")
        self.frame.pack(fill="both", expand=True)

        self._build_ui()
        self.load_tables()
        self.load_products()

    def _build_ui(self):
        top = tk.Frame(self.frame, bg="white")
        top.pack(fill="x", padx=14, pady=10)

        tk.Label(top, text="Bàn:", bg="white", font=("Arial", 11, "bold")).pack(side="left")
        self.table_var = tk.StringVar()
        self.table_menu = tk.OptionMenu(top, self.table_var, "")
        self.table_menu.config(width=18)
        self.table_menu.pack(side="left", padx=6)

        tk.Label(top, text="Số lượng:", bg="white", font=("Arial", 11, "bold")).pack(side="left", padx=(8, 0))
        self.qty_var = tk.StringVar(value="1")
        tk.Entry(top, textvariable=self.qty_var, width=5).pack(side="left", padx=6)

        tk.Button(top, text="Thêm vào order", bg="#2ecc71", fg="white", command=self.add_to_order).pack(side="left", padx=8)
        tk.Button(top, text="Xem order", command=self.show_current_order).pack(side="left", padx=4)
        tk.Button(top, text="Xuất hóa đơn & Thanh toán", bg="#f39c12", fg="white", command=self.export_invoice).pack(side="left", padx=4)

        body = tk.Frame(self.frame, bg="white")
        body.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        left = tk.Frame(body, bg="#f8f8f8", bd=1, relief="solid")
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))

        tk.Label(left, text="Danh sách món", bg="#f8f8f8", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=8)

        grid_wrap = tk.Frame(left, bg="#f8f8f8")
        grid_wrap.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.product_canvas = tk.Canvas(grid_wrap, bg="#f8f8f8", highlightthickness=0)
        self.product_scrollbar = tk.Scrollbar(grid_wrap, orient="vertical", command=self.product_canvas.yview)
        self.product_canvas.configure(yscrollcommand=self.product_scrollbar.set)
        self.product_canvas.pack(side="left", fill="both", expand=True)
        self.product_scrollbar.pack(side="right", fill="y")

        self.product_grid = tk.Frame(self.product_canvas, bg="#f8f8f8")
        self.product_canvas_window = self.product_canvas.create_window((0, 0), window=self.product_grid, anchor="nw")
        self.product_grid.bind("<Configure>", lambda _e: self.product_canvas.configure(scrollregion=self.product_canvas.bbox("all")))
        self.product_canvas.bind("<Configure>", self._on_product_canvas_resize)

        self.product_form = tk.Frame(left, bg="#f8f8f8")
        self.product_form.pack(fill="x", padx=10, pady=(0, 10))

        tk.Label(self.product_form, text="Tên món", bg="#f8f8f8").grid(row=0, column=0, sticky="w")
        tk.Label(self.product_form, text="Giá", bg="#f8f8f8").grid(row=0, column=1, sticky="w")
        tk.Label(self.product_form, text="Ảnh", bg="#f8f8f8").grid(row=2, column=0, sticky="w", pady=(4, 0))
        self.product_name_var = tk.StringVar()
        self.product_price_var = tk.StringVar()
        self.product_status_var = tk.StringVar(value="Còn bán")
        self.product_image_var = tk.StringVar()
        tk.Entry(self.product_form, textvariable=self.product_name_var, width=22).grid(row=1, column=0, padx=(0, 8), pady=4)
        tk.Entry(self.product_form, textvariable=self.product_price_var, width=10).grid(row=1, column=1, pady=4)
        tk.OptionMenu(self.product_form, self.product_status_var, "Còn bán", "Hết món").grid(row=1, column=2, padx=8)
        tk.Entry(self.product_form, textvariable=self.product_image_var, width=26).grid(row=3, column=0, columnspan=2, sticky="we")
        tk.Button(self.product_form, text="Chọn ảnh", command=self.pick_product_image).grid(row=3, column=2, padx=8)

        actions = tk.Frame(self.product_form, bg="#f8f8f8")
        actions.grid(row=1, column=3)
        self.btn_add = tk.Button(actions, text="Thêm", command=self.add_product)
        self.btn_add.pack(side="left", padx=2)
        self.btn_update = tk.Button(actions, text="Sửa", command=self.update_product_info)
        self.btn_update.pack(side="left", padx=2)
        self.btn_delete = tk.Button(actions, text="Xóa", command=self.delete_product_info)
        self.btn_delete.pack(side="left", padx=2)
        self.image_preview_label = tk.Label(self.product_form, text="(Chưa có ảnh)", bg="#f8f8f8", fg="#666")
        self.image_preview_label.grid(row=3, column=3, padx=8)

        right = tk.Frame(body, bg="#eef6ff", bd=1, relief="solid", width=360)
        right.pack(side="right", fill="both")
        right.pack_propagate(False)

        tk.Label(right, text="Chi tiết order", bg="#eef6ff", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=8)
        self.order_text = tk.Text(right, height=26, bg="#eef6ff", relief="flat", font=("Consolas", 10))
        self.order_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        if self.role != "Admin":
            self.btn_add.config(state="disabled")
            self.btn_update.config(state="disabled")
            self.btn_delete.config(state="disabled")
            self.product_name_var.set("(Chỉ admin được CRUD món)")

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

    def load_products(self):
        self.products = get_all_products()
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
        self.refresh_image_preview(product[4])
        self._refresh_selected_card()

    def _on_product_canvas_resize(self, event):
        self.product_canvas.itemconfig(self.product_canvas_window, width=event.width)

    def render_product_cards(self):
        for widget in self.product_grid.winfo_children():
            widget.destroy()

        self.card_image_cache = {}
        self.product_cards = {}
        card_width = 140
        columns = 4

        for idx, product in enumerate(self.products):
            row = idx // columns
            column = idx % columns
            card = tk.Frame(
                self.product_grid,
                bg="white",
                bd=1,
                relief="solid",
                width=card_width,
                height=180,
                cursor="hand2",
                padx=8,
                pady=8,
            )
            card.grid(row=row, column=column, padx=6, pady=6, sticky="n")
            card.grid_propagate(False)

            image = self._build_product_image(product[4], width=110, height=78)
            image_label = tk.Label(card, image=image, bg="white")
            image_label.image = image
            image_label.pack(pady=(0, 8))

            name_label = tk.Label(
                card,
                text=product[1],
                bg="white",
                font=("Arial", 10, "bold"),
                wraplength=116,
                justify="center",
            )
            name_label.pack(fill="x")

            price_label = tk.Label(
                card,
                text=f"{product[2]:,.0f}đ",
                bg="white",
                fg="#1b8dd8",
                font=("Arial", 10, "bold"),
            )
            price_label.pack(pady=(4, 0))

            if product[3] == "Hết món":
                sold_out = tk.Label(card, text="HẾT MÓN", bg="#fce6e6", fg="#c0392b", font=("Arial", 9, "bold"))
                sold_out.pack(pady=(8, 0), fill="x")

            self._bind_card_click(card, product[0])
            self._bind_card_click(image_label, product[0])
            self._bind_card_click(name_label, product[0])
            self._bind_card_click(price_label, product[0])
            self.product_cards[product[0]] = card

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
                card.configure(bg="#e9f4ff", bd=2, relief="solid")
            else:
                card.configure(bg="white", bd=1, relief="solid")

    def _build_product_image(self, image_path, width=110, height=78):
        cache_key = f"{image_path}|{width}x{height}"
        if cache_key in self.card_image_cache:
            return self.card_image_cache[cache_key]

        image = None
        resolved_path = self._resolve_image_path(image_path)
        if resolved_path:
            try:
                image = tk.PhotoImage(file=resolved_path)
            except tk.TclError:
                image = None

        if image:
            image = image.subsample(max(1, image.width() // width), max(1, image.height() // height))
        else:
            image = tk.PhotoImage(width=width, height=height)
            image.put("#d9d9d9", to=(0, 0, width, height))

        self.card_image_cache[cache_key] = image
        return image

    def _resolve_image_path(self, image_path):
        if not image_path:
            return None

        raw_path = image_path.strip()
        normalized_candidates = {
            os.path.normpath(raw_path),
            os.path.normpath(raw_path.replace("\\", os.sep)),
            os.path.normpath(raw_path.replace("/", os.sep)),
        }

        for normalized_path in normalized_candidates:
            if os.path.isabs(normalized_path) and os.path.exists(normalized_path):
                return normalized_path

            local_candidate = os.path.normpath(os.path.join(os.getcwd(), normalized_path))
            if os.path.exists(local_candidate):
                return local_candidate

            project_candidate = os.path.normpath(os.path.join(self.project_root, normalized_path))
            if os.path.exists(project_candidate):
                return project_candidate

        return None

    def _selected_table_id(self):
        raw = self.table_var.get().strip()
        if not raw:
            return None
        return int(raw.split("-")[0].strip())

    def add_product(self):
        if self.role != "Admin":
            return
        name = self.product_name_var.get().strip()
        status = self.product_status_var.get()
        try:
            price = float(self.product_price_var.get().strip())
        except ValueError:
            messagebox.showwarning("Sai dữ liệu", "Giá món không hợp lệ")
            return
        if not name:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập tên món")
            return
        create_product(name, price, status, self.product_image_var.get().strip() or None)
        self.load_products()

    def update_product_info(self):
        if self.role != "Admin" or not self.selected_product_id:
            return
        name = self.product_name_var.get().strip()
        status = self.product_status_var.get()
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
        )
        self.load_products()

    def delete_product_info(self):
        if self.role != "Admin" or not self.selected_product_id:
            return
        if not messagebox.askyesno("Xác nhận", "Xóa món đã chọn?"):
            return
        delete_product(self.selected_product_id)
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
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif"), ("All files", "*.*")],
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
        resolved_path = self._resolve_image_path(image_path)
        if not resolved_path:
            self.current_image_preview = None
            self.image_preview_label.configure(image="", text="(Chưa có ảnh)")
            return

        try:
            preview = tk.PhotoImage(file=resolved_path)
            self.current_image_preview = preview
            self.image_preview_label.configure(image=preview, text="")
        except tk.TclError:
            self.current_image_preview = None
            self.image_preview_label.configure(image="", text="(Không preview được, vẫn lưu đường dẫn)")
