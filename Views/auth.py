import tkinter as tk
from tkinter import messagebox

from Config.db import get_connection


class AuthView:
    def __init__(self, root, on_login_success):
        self.root = root
        self.on_login_success = on_login_success
        self.mode = "signin"

        self.frame = tk.Frame(root, bg="#0a0c16")
        self.frame.pack(expand=True, fill="both")

        self._build_ui()

    def _build_ui(self):
        container = tk.Frame(self.frame, bg="#05070f", padx=30, pady=25)
        container.place(relx=0.5, rely=0.5, anchor="center", width=760, height=420)

        # Left panel (illustration substitute)
        left_panel = tk.Frame(container, bg="#05070f")
        left_panel.pack(side="left", fill="both", expand=True)

        tk.Label(
            left_panel,
            text="WELCOME",
            bg="#05070f",
            fg="white",
            font=("Arial", 20, "bold"),
        ).pack(anchor="nw")

        tk.Label(
            left_panel,
            text="☕",
            bg="#05070f",
            fg="#1fb6ff",
            font=("Arial", 82),
        ).pack(expand=True)

        # Right panel (form)
        right_panel = tk.Frame(container, bg="#05070f")
        right_panel.pack(side="right", fill="both", expand=True, padx=(25, 0))

        self.title_label = tk.Label(
            right_panel,
            text="Sign In",
            bg="#05070f",
            fg="white",
            font=("Arial", 18, "bold"),
        )
        self.title_label.pack(pady=(15, 22))

        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()

        self._create_labeled_entry(right_panel, "Username", self.username_var)
        self._create_labeled_entry(right_panel, "Password", self.password_var, show="*")

        self.action_btn = tk.Button(
            right_panel,
            text="LOGIN",
            bg="#2a43ff",
            fg="white",
            relief="flat",
            font=("Arial", 11, "bold"),
            cursor="hand2",
            command=self._handle_action,
        )
        self.action_btn.pack(fill="x", pady=(16, 8), ipady=6)

        self.helper_label = tk.Label(
            right_panel,
            text="No account yet?",
            bg="#05070f",
            fg="#d6d6d6",
            font=("Arial", 10),
        )
        self.helper_label.pack(side="left", pady=(10, 0))

        self.toggle_btn = tk.Button(
            right_panel,
            text="SIGN UP NOW",
            bg="#17a2b8",
            fg="white",
            relief="flat",
            cursor="hand2",
            font=("Arial", 9, "bold"),
            command=self._toggle_mode,
        )
        self.toggle_btn.pack(side="right", pady=(10, 0))

    def _create_labeled_entry(self, parent, label, variable, show=None):
        tk.Label(
            parent,
            text=label,
            bg="#05070f",
            fg="#c5c5c5",
            font=("Arial", 10),
        ).pack(anchor="w", pady=(0, 4))

        entry = tk.Entry(
            parent,
            textvariable=variable,
            bg="#0b1021",
            fg="white",
            insertbackground="white",
            relief="flat",
            show=show,
            font=("Arial", 11),
        )
        entry.pack(fill="x", pady=(0, 14), ipady=8)

    def _toggle_mode(self):
        self.mode = "signup" if self.mode == "signin" else "signin"

        if self.mode == "signin":
            self.title_label.config(text="Sign In")
            self.action_btn.config(text="LOGIN")
            self.helper_label.config(text="No account yet?")
            self.toggle_btn.config(text="SIGN UP NOW")
        else:
            self.title_label.config(text="Sign Up")
            self.action_btn.config(text="REGISTER")
            self.helper_label.config(text="Already have account?")
            self.toggle_btn.config(text="SIGN IN")

    def _handle_action(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()

        if not username or not password:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đủ tài khoản và mật khẩu.")
            return

        if self.mode == "signin":
            self._login(username, password)
        else:
            self._signup(username, password)

    def _login(self, username, password):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT Username, Role FROM Users WHERE Username = ? AND Password = ?",
            (username, password),
        )
        user = cursor.fetchone()
        conn.close()

        if user:
            self.destroy()
            self.on_login_success(user[0], user[1])
        else:
            messagebox.showerror("Đăng nhập thất bại", "Sai tên đăng nhập hoặc mật khẩu.")

    def _signup(self, username, password):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO Users (Username, Password, Role) VALUES (?, ?, 'Staff')",
                (username, password),
            )
            conn.commit()
            messagebox.showinfo("Thành công", "Đăng ký thành công. Mời bạn đăng nhập.")
            self._toggle_mode()
            self.password_var.set("")
        except Exception as e:
            messagebox.showerror("Đăng ký thất bại", f"Không thể tạo tài khoản: {e}")
        finally:
            conn.close()

    def destroy(self):
        self.frame.destroy()
