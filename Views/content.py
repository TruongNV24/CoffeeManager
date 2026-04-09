import tkinter as tk

class ContentView:
    def __init__(self, root):
        self.frame = tk.Frame(root, bg="white")
        self.frame.pack(side="right", expand=True, fill="both")

    def clear(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

    def show_text(self, text):
        self.clear()
        label = tk.Label(self.frame, text=text, font=("Arial", 20))
        label.pack(pady=50)