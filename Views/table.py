import tkinter as tk
from controllers.table import TableController

class TableView:
    def __init__(self, root):
        self.root = root
        self.controller = TableController()

        self.frame = tk.Frame(root)
        self.frame.pack(fill="both", expand=True)

        self.load_tables()

    def load_tables(self):
        tables = self.controller.load_tables()

        for index, table in enumerate(tables):
            table_id = table[0]
            name = table[1]
            status = table[2]

            color = "green" if status == "Trống" else "red"

            btn = tk.Button(
                self.frame,
                text=name,
                bg=color,
                width=15,
                height=3,
                command=lambda id=table_id: self.open_table(id)
            )

            btn.grid(row=index//4, column=index%4, padx=10, pady=10)

    def open_table(self, table_id):
        order = self.controller.open_table(table_id)

        if order:
            print("Mở order hiện tại:", order)
        else:
            print("Tạo order mới")