import tkinter as tk
from tkinter import ttk
from datetime import datetime

from Controllers.report import ReportService
from Views.theme import COLORS, FONT_FAMILY, button


class ReportView:
    def __init__(self, parent):
        self.parent = parent
        self.service = ReportService()
        self.frame = tk.Frame(parent, bg=COLORS["app_bg"])
        self.frame.pack(fill="both", expand=True)

        self.year_var = tk.StringVar(value=str(datetime.now().year))
        self.month_var = tk.StringVar(value=f"{datetime.now().month:02d}")
        self.mode_var = tk.StringVar(value="month")

        self._build_ui()
        self.load_report()

    def _build_ui(self):
        header = tk.Frame(self.frame, bg=COLORS["app_bg"])
        header.pack(fill="x", padx=24, pady=(20, 6))
        tk.Label(header, text="📊 Báo cáo doanh thu", bg=COLORS["app_bg"], fg=COLORS["text"], font=(FONT_FAMILY, 24, "bold")).pack(anchor="w")
        tk.Label(header, text="Theo dõi doanh thu và hiệu suất quán", bg=COLORS["app_bg"], fg=COLORS["muted"], font=(FONT_FAMILY, 10)).pack(anchor="w")

        filter_bar = tk.Frame(self.frame, bg=COLORS["surface"], padx=14, pady=12, highlightthickness=1, highlightbackground=COLORS["border"])
        filter_bar.pack(fill="x", padx=24, pady=(0, 12))
        tk.Label(filter_bar, text="Năm", bg=COLORS["surface"], fg=COLORS["muted"]).pack(side="left")
        years = [str(y) for y in range(datetime.now().year - 5, datetime.now().year + 1)]
        ttk.Combobox(filter_bar, textvariable=self.year_var, values=years, width=8, state="readonly").pack(side="left", padx=(6, 16))
        tk.Label(filter_bar, text="Tháng", bg=COLORS["surface"], fg=COLORS["muted"]).pack(side="left")
        ttk.Combobox(filter_bar, textvariable=self.month_var, values=[f"{m:02d}" for m in range(1, 13)], width=6, state="readonly").pack(side="left", padx=(6, 16))
        ttk.Radiobutton(filter_bar, text="Theo tháng", variable=self.mode_var, value="month").pack(side="left", padx=(2, 8))
        ttk.Radiobutton(filter_bar, text="Theo năm", variable=self.mode_var, value="year").pack(side="left")
        button(filter_bar, text="Xem báo cáo", command=self.load_report).pack(side="right")

        self.cards_frame = tk.Frame(self.frame, bg=COLORS["app_bg"])
        self.cards_frame.pack(fill="x", padx=24, pady=(0, 10))

        chart_wrap = tk.Frame(self.frame, bg=COLORS["surface"], padx=16, pady=12, highlightthickness=1, highlightbackground=COLORS["border"])
        chart_wrap.pack(fill="both", expand=True, padx=24, pady=(0, 12))
        tk.Label(chart_wrap, text="Biểu đồ doanh thu", bg=COLORS["surface"], fg=COLORS["text"], font=(FONT_FAMILY, 12, "bold")).pack(anchor="w")
        self.chart = tk.Canvas(chart_wrap, bg=COLORS["white"], height=260, highlightthickness=0)
        self.chart.pack(fill="x", pady=(10, 6))
        self.chart.bind("<Configure>", lambda _e: self.LoadRevenueChart())

        invoice_wrap = tk.Frame(self.frame, bg=COLORS["surface"], padx=16, pady=12, highlightthickness=1, highlightbackground=COLORS["border"])
        invoice_wrap.pack(fill="both", expand=True, padx=24, pady=(0, 20))
        tk.Label(invoice_wrap, text="Danh sách hóa đơn", bg=COLORS["surface"], fg=COLORS["text"], font=(FONT_FAMILY, 12, "bold")).pack(anchor="w")

        cols = ("id", "table", "time", "total", "staff")
        self.invoice_table = ttk.Treeview(invoice_wrap, columns=cols, show="headings", height=8)
        self.invoice_table.heading("id", text="Mã hóa đơn")
        self.invoice_table.heading("table", text="Bàn")
        self.invoice_table.heading("time", text="Thời gian")
        self.invoice_table.heading("total", text="Tổng tiền")
        self.invoice_table.heading("staff", text="Nhân viên")
        self.invoice_table.column("id", width=120, anchor="center")
        self.invoice_table.column("table", width=120, anchor="center")
        self.invoice_table.column("time", width=240)
        self.invoice_table.column("total", width=140, anchor="e")
        self.invoice_table.column("staff", width=170)
        self.invoice_table.pack(fill="both", expand=True, pady=(8, 0))
        self.invoice_table.tag_configure("even", background="#FFF9F4")

    def load_report(self):
        self.LoadStatisticsCards()
        self.LoadRevenueChart()
        self.LoadInvoiceTable()

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
        h = max(self.chart.winfo_height(), 240)
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

    def LoadInvoiceTable(self):
        for row in self.invoice_table.get_children():
            self.invoice_table.delete(row)
        month = self.month_var.get() if self.mode_var.get() == "month" else None
        for idx, row in enumerate(self.service.get_invoices(self.year_var.get(), month)):
            tags = ("even",) if idx % 2 == 0 else ()
            self.invoice_table.insert("", "end", values=(row[0], row[1], row[2], f"{row[3]:,.0f}đ", row[4]), tags=tags)
