import os
import threading
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, ttk

from Controllers.excel_export import ExcelExportService
from Controllers.report import ReportService
from Views.theme import COLORS, FONT_FAMILY, button


class ScrollableReportContainer:
    def __init__(self, parent):
        self.main_content_container = tk.Frame(parent, bg=COLORS["app_bg"])
        self.main_content_container.pack(fill="both", expand=True)
        self.main_content_container.grid_rowconfigure(0, weight=1)
        self.main_content_container.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            self.main_content_container,
            bg=COLORS["app_bg"],
            highlightthickness=0,
            bd=0,
        )
        self.scrollbar = ttk.Scrollbar(
            self.main_content_container,
            orient="vertical",
            command=self.canvas.yview,
        )
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        self.inner_frame = tk.Frame(self.canvas, bg=COLORS["app_bg"])
        self.window_id = self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.inner_frame.bind("<Configure>", self.configure_scroll_region)
        self._bind_mousewheel()

    def _on_canvas_configure(self, event):
        self.canvas.itemconfigure(self.window_id, width=event.width)
        self.configure_scroll_region()

    def configure_scroll_region(self, _event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _bind_mousewheel(self):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel, add="+")
        self.canvas.bind_all("<Button-4>", self._on_mousewheel_linux, add="+")
        self.canvas.bind_all("<Button-5>", self._on_mousewheel_linux, add="+")

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_mousewheel_linux(self, event):
        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")


class ReportView:
    CHART_HEIGHT = 400

    def __init__(self, parent):
        self.parent = parent
        self.service = ReportService()
        self.excel_service = ExcelExportService()
        self.frame = tk.Frame(parent, bg=COLORS["app_bg"])
        self.frame.pack(fill="both", expand=True)

        self.year_var = tk.StringVar(value=str(datetime.now().year))
        self.month_var = tk.StringVar(value=f"{datetime.now().month:02d}")
        self.mode_var = tk.StringVar(value="month")

        self.setup_scrollable_content()
        self._build_ui()
        self.load_report()

    def setup_scrollable_content(self):
        self.scroll_container = ScrollableReportContainer(self.frame)
        self.content_frame = self.scroll_container.inner_frame

    def configure_scroll_region(self, _event=None):
        self.scroll_container.configure_scroll_region()

    def _build_ui(self):
        header = tk.Frame(self.content_frame, bg=COLORS["app_bg"])
        header.pack(fill="x", padx=24, pady=(20, 10))
        tk.Label(header, text="📊 Báo cáo doanh thu", bg=COLORS["app_bg"], fg=COLORS["text"], font=(FONT_FAMILY, 24, "bold")).pack(anchor="w")
        tk.Label(header, text="Theo dõi doanh thu và hiệu suất quán", bg=COLORS["app_bg"], fg=COLORS["muted"], font=(FONT_FAMILY, 10)).pack(anchor="w")

        filter_bar = tk.Frame(self.content_frame, bg=COLORS["surface"], padx=14, pady=12, highlightthickness=1, highlightbackground=COLORS["border"])
        filter_bar.pack(fill="x", padx=24, pady=(0, 14))
        tk.Label(filter_bar, text="Năm", bg=COLORS["surface"], fg=COLORS["muted"]).pack(side="left")
        years = [str(y) for y in range(datetime.now().year - 5, datetime.now().year + 1)]
        ttk.Combobox(filter_bar, textvariable=self.year_var, values=years, width=8, state="readonly").pack(side="left", padx=(6, 16))
        tk.Label(filter_bar, text="Tháng", bg=COLORS["surface"], fg=COLORS["muted"]).pack(side="left")
        ttk.Combobox(filter_bar, textvariable=self.month_var, values=[f"{m:02d}" for m in range(1, 13)], width=6, state="readonly").pack(side="left", padx=(6, 16))
        ttk.Radiobutton(filter_bar, text="Theo tháng", variable=self.mode_var, value="month").pack(side="left", padx=(2, 8))
        ttk.Radiobutton(filter_bar, text="Theo năm", variable=self.mode_var, value="year").pack(side="left")
        button(filter_bar, text="Xem báo cáo", command=self.load_report).pack(side="right")

        self.cards_frame = tk.Frame(self.content_frame, bg=COLORS["app_bg"])
        self.cards_frame.pack(fill="x", padx=24, pady=(0, 14))

        self.chart_section = tk.Frame(self.content_frame, bg=COLORS["surface"], padx=16, pady=12, highlightthickness=1, highlightbackground=COLORS["border"], height=self.CHART_HEIGHT + 70)
        self.chart_section.pack(fill="x", padx=24, pady=(0, 14))
        self.chart_section.pack_propagate(False)
        tk.Label(self.chart_section, text="Biểu đồ doanh thu", bg=COLORS["surface"], fg=COLORS["text"], font=(FONT_FAMILY, 12, "bold")).pack(anchor="w")
        self.chart = tk.Canvas(self.chart_section, bg=COLORS["white"], height=self.CHART_HEIGHT, highlightthickness=0)
        self.chart.pack(fill="x", expand=False, pady=(10, 6))
        self.chart.bind("<Configure>", lambda _e: self.LoadRevenueChart())

        self._build_export_card()
        self.content_frame.bind("<Configure>", self.configure_scroll_region)

    def _build_export_card(self):
        shadow = tk.Frame(self.content_frame, bg="#D9C7B7")
        shadow.pack(fill="x", padx=28, pady=(0, 24))

        export_wrap = tk.Frame(shadow, bg=COLORS["surface"], padx=18, pady=16, highlightthickness=1, highlightbackground=COLORS["border"])
        export_wrap.pack(fill="x", padx=(0, 2), pady=(0, 2))

        tk.Label(export_wrap, text="📁 Xuất báo cáo Excel", bg=COLORS["surface"], fg=COLORS["text"], font=(FONT_FAMILY, 12, "bold")).grid(row=0, column=0, columnspan=7, sticky="w")
        tk.Label(export_wrap, text="📊", bg=COLORS["surface"], fg="#1D6F42", font=(FONT_FAMILY, 22, "bold")).grid(row=1, column=0, padx=(0, 8), pady=(12, 0))
        tk.Label(export_wrap, text="Tháng", bg=COLORS["surface"], fg=COLORS["muted"]).grid(row=1, column=1, sticky="w", pady=(12, 0))
        self.export_month_combo = ttk.Combobox(export_wrap, textvariable=self.month_var, values=[f"{m:02d}" for m in range(1, 13)], width=8, state="readonly")
        self.export_month_combo.grid(row=1, column=2, padx=(6, 14), pady=(12, 0))
        tk.Label(export_wrap, text="Năm", bg=COLORS["surface"], fg=COLORS["muted"]).grid(row=1, column=3, sticky="w", pady=(12, 0))
        self.export_year_combo = ttk.Combobox(export_wrap, textvariable=self.year_var, values=[str(y) for y in range(datetime.now().year - 5, datetime.now().year + 1)], width=8, state="readonly")
        self.export_year_combo.grid(row=1, column=4, padx=(6, 14), pady=(12, 0))
        self.export_btn = button(export_wrap, text="Xuất Excel", command=self.export_monthly_report)
        self.export_btn.grid(row=1, column=5, padx=(8, 0), pady=(12, 0))
        export_wrap.grid_columnconfigure(6, weight=1)

    def load_report(self):
        self.LoadStatisticsCards()
        self.LoadRevenueChart()
        self.configure_scroll_region()

    def export_monthly_report(self):
        month, year = self.month_var.get(), self.year_var.get()
        daily_rows = self.service.get_daily_revenue_details(year, month)
        if not daily_rows:
            messagebox.showinfo("Không có dữ liệu", f"Không có dữ liệu doanh thu cho tháng {int(month)}/{year}.")
            return

        output_dir = filedialog.askdirectory(title="Chọn thư mục lưu báo cáo Excel")
        if not output_dir:
            return

        self.export_btn.config(state="disabled")
        threading.Thread(target=self._run_export, args=(month, year, output_dir), daemon=True).start()

    def _run_export(self, month, year, output_dir):
        try:
            stats = self.service.get_statistics(year, month)
            daily_rows = self.service.get_daily_revenue_details(year, month)
            file_path = self.excel_service.ExportMonthlyReport(month, year, stats, daily_rows, output_dir)
            self.frame.after(0, lambda: self._on_export_success(file_path))
        except Exception as exc:
            self.frame.after(0, lambda: self._on_export_error(exc))

    def _on_export_success(self, file_path):
        self.export_btn.config(state="normal")
        if messagebox.askyesno("Xuất thành công", f"Đã xuất file:\n{file_path}\n\nBạn có muốn mở thư mục chứa file không?"):
            os.startfile(os.path.dirname(file_path))

    def _on_export_error(self, exc):
        self.export_btn.config(state="normal")
        messagebox.showerror("Lỗi xuất Excel", f"Không thể xuất báo cáo: {exc}")

    def LoadStatisticsCards(self):
        for w in self.cards_frame.winfo_children():
            w.destroy()
        month = self.month_var.get() if self.mode_var.get() == "month" else None
        stats = self.service.get_statistics(self.year_var.get(), month)
        cards = [
            ("💸 Tổng doanh thu", f"{stats['revenue']:,.0f}đ"),
            ("🧾 Tổng hóa đơn", str(stats["invoice_count"])),
            ("🍰 Tổng món bán", str(stats["total_items"])),
            ("🔥 Bàn hoạt động nhiều", stats["top_table"]),
        ]
        for i, (title, value) in enumerate(cards):
            card = tk.Frame(self.cards_frame, bg=COLORS["surface"], padx=16, pady=14, highlightthickness=1, highlightbackground=COLORS["border"])
            card.grid(row=0, column=i, sticky="nsew", padx=6)
            tk.Label(card, text=title, bg=COLORS["surface"], fg=COLORS["muted"], font=(FONT_FAMILY, 10, "bold")).pack(anchor="w")
            tk.Label(card, text=value, bg=COLORS["surface"], fg=COLORS["primary_dark"], font=(FONT_FAMILY, 16, "bold")).pack(anchor="w", pady=(8, 0))
            self.cards_frame.grid_columnconfigure(i, weight=1)

    def LoadRevenueChart(self):
        if not hasattr(self, "chart"):
            return
        self.chart.delete("all")
        month = self.month_var.get() if self.mode_var.get() == "month" else None
        labels, values = self.service.get_revenue_series(self.year_var.get(), month)
        w = max(self.chart.winfo_width(), 500)
        h = self.CHART_HEIGHT
        self.chart.create_rectangle(45, 10, w - 12, h - 28, outline=COLORS["border"])
        if not values:
            self.chart.create_text(w / 2, h / 2, text="Chưa có dữ liệu doanh thu.", fill=COLORS["muted"], font=(FONT_FAMILY, 11, "italic"))
            return
        max_v = max(values) or 1
        step = max((w - 80) / max(len(values) - 1, 1), 35)
        points = []
        for idx, value in enumerate(values):
            x = 55 + idx * step
            y = (h - 40) - ((value / max_v) * (h - 70))
            points.extend([x, y])
            self.chart.create_text(x, h - 16, text=labels[idx], fill=COLORS["muted"], font=(FONT_FAMILY, 8))
        self.chart.create_line(*points, fill=COLORS["primary"], width=3, smooth=True)
        for idx, value in enumerate(values):
            x, y = points[idx * 2], points[idx * 2 + 1]
            self.chart.create_oval(x - 3, y - 3, x + 3, y + 3, fill=COLORS["primary_dark"], outline="")
            self.chart.create_text(x, y - 12, text=f"{value:,.0f}", fill=COLORS["primary_dark"], font=(FONT_FAMILY, 8, "bold"))
