"""
Login View using CustomTkinter.
Provides Staff/Admin authentication interface with quick-fill demo buttons for case study defense.
"""

import customtkinter as ctk
from controllers.auth_controller import AuthController


class LoginView(ctk.CTkFrame):
    def __init__(self, master, on_login_success):
        super().__init__(master, corner_radius=15)
        self.master = master
        self.on_login_success = on_login_success
        self.auth_controller = AuthController()

        self._build_ui()

    def _build_ui(self):
        # Outer layout: Centered card
        self.grid_columnconfigure(0, weight=1)

        # Title / Brand
        brand_label = ctk.CTkLabel(
            self,
            text="🐾 PurrfectMatch",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        brand_label.grid(row=0, column=0, padx=30, pady=(30, 5))

        subtitle_label = ctk.CTkLabel(
            self,
            text="Cat Adoption & Shelter Management System",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        subtitle_label.grid(row=1, column=0, padx=30, pady=(0, 25))

        login_header = ctk.CTkLabel(
            self,
            text="Staff / Administrator Login",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        login_header.grid(row=2, column=0, padx=30, pady=(0, 15))

        # Username Input
        self.username_entry = ctk.CTkEntry(
            self,
            width=280,
            height=40,
            placeholder_text="Username"
        )
        self.username_entry.grid(row=3, column=0, padx=30, pady=8)
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())

        # Password Input
        self.password_entry = ctk.CTkEntry(
            self,
            width=280,
            height=40,
            placeholder_text="Password",
            show="•"
        )
        self.password_entry.grid(row=4, column=0, padx=30, pady=8)
        self.password_entry.bind("<Return>", lambda e: self._handle_login())

        # Error / Feedback Message Label
        self.feedback_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="#e74c3c"
        )
        self.feedback_label.grid(row=5, column=0, padx=30, pady=(5, 5))

        # Login Button
        self.login_btn = ctk.CTkButton(
            self,
            text="Log In",
            width=280,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._handle_login
        )
        self.login_btn.grid(row=6, column=0, padx=30, pady=(10, 15))

        # Quick Fill Helpers (Great for presentation / case study defense)
        quick_fill_frame = ctk.CTkFrame(self, fg_color="transparent")
        quick_fill_frame.grid(row=7, column=0, padx=30, pady=(5, 25))

        admin_fill_btn = ctk.CTkButton(
            quick_fill_frame,
            text="Fill Admin",
            width=135,
            height=30,
            fg_color="#34495e",
            hover_color="#2c3e50",
            command=lambda: self._quick_fill("admin", "admin123")
        )
        admin_fill_btn.pack(side="left", padx=5)

        staff_fill_btn = ctk.CTkButton(
            quick_fill_frame,
            text="Fill Staff",
            width=135,
            height=30,
            fg_color="#34495e",
            hover_color="#2c3e50",
            command=lambda: self._quick_fill("staff", "staff123")
        )
        staff_fill_btn.pack(side="left", padx=5)

    def _quick_fill(self, user, pwd):
        self.username_entry.delete(0, "end")
        self.username_entry.insert(0, user)
        self.password_entry.delete(0, "end")
        self.password_entry.insert(0, pwd)
        self.feedback_label.configure(text="")

    def _handle_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        success, result = self.auth_controller.login(username, password)
        if success:
            self.feedback_label.configure(text="Login successful!", text_color="#2ecc71")
            self.on_login_success(result)
        else:
            self.feedback_label.configure(text=result, text_color="#e74c3c")
