"""
Login View using CustomTkinter.
Provides Staff/Admin authentication interface with quick-fill demo buttons for case study defense.
"""

import customtkinter as ctk
from views.theme import Theme
from controllers.auth_controller import AuthController


class LoginView(ctk.CTkFrame):
    def __init__(self, master, on_login_success):
        super().__init__(
            master,
            corner_radius=Theme.RADIUS_CARD,
            fg_color=Theme.BG_CARD,
            border_width=1,
            border_color=Theme.BORDER
        )
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
            font=Theme.font_hero(),
            text_color=Theme.TEXT_PRIMARY
        )
        brand_label.grid(row=0, column=0, padx=36, pady=(32, 4))

        subtitle_label = ctk.CTkLabel(
            self,
            text="Cat Adoption & Shelter Management System",
            font=Theme.font_caption(),
            text_color=Theme.TEXT_MUTED
        )
        subtitle_label.grid(row=1, column=0, padx=36, pady=(0, 24))

        login_header = ctk.CTkLabel(
            self,
            text="Staff / Administrator Portal",
            font=Theme.font_subtitle(),
            text_color=Theme.TEXT_PRIMARY
        )
        login_header.grid(row=2, column=0, padx=36, pady=(0, 16))

        # Username Input
        self.username_entry = ctk.CTkEntry(
            self,
            width=290,
            height=38,
            corner_radius=Theme.RADIUS_INPUT,
            fg_color=Theme.BG_INPUT,
            border_color=Theme.BORDER,
            text_color=Theme.TEXT_PRIMARY,
            placeholder_text_color=Theme.TEXT_MUTED,
            placeholder_text="Username"
        )
        self.username_entry.grid(row=3, column=0, padx=36, pady=6)
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())

        # Password Input
        self.password_entry = ctk.CTkEntry(
            self,
            width=290,
            height=38,
            corner_radius=Theme.RADIUS_INPUT,
            fg_color=Theme.BG_INPUT,
            border_color=Theme.BORDER,
            text_color=Theme.TEXT_PRIMARY,
            placeholder_text_color=Theme.TEXT_MUTED,
            placeholder_text="Password",
            show="•"
        )
        self.password_entry.grid(row=4, column=0, padx=36, pady=6)
        self.password_entry.bind("<Return>", lambda e: self._handle_login())

        # Error / Feedback Message Label
        self.feedback_label = ctk.CTkLabel(
            self,
            text="",
            font=Theme.font_caption(),
            text_color=Theme.DANGER
        )
        self.feedback_label.grid(row=5, column=0, padx=36, pady=(4, 4))

        # Login Button
        self.login_btn = ctk.CTkButton(
            self,
            text="Sign In",
            width=290,
            height=38,
            corner_radius=Theme.RADIUS_BTN,
            font=Theme.font_body_bold(),
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            text_color=Theme.PRIMARY_TEXT,
            command=self._handle_login
        )
        self.login_btn.grid(row=6, column=0, padx=36, pady=(8, 16))

        # Quick Fill Helpers (Great for presentation / case study defense)
        quick_fill_frame = ctk.CTkFrame(self, fg_color="transparent")
        quick_fill_frame.grid(row=7, column=0, padx=36, pady=(0, 28))

        admin_fill_btn = ctk.CTkButton(
            quick_fill_frame,
            text="Fill Admin",
            width=140,
            height=30,
            corner_radius=Theme.RADIUS_BTN,
            font=Theme.font_caption_bold(),
            fg_color=Theme.SECONDARY,
            hover_color=Theme.SECONDARY_HOVER,
            text_color=Theme.SECONDARY_TEXT,
            command=lambda: self._quick_fill("admin", "admin123")
        )
        admin_fill_btn.pack(side="left", padx=5)

        staff_fill_btn = ctk.CTkButton(
            quick_fill_frame,
            text="Fill Staff",
            width=140,
            height=30,
            corner_radius=Theme.RADIUS_BTN,
            font=Theme.font_caption_bold(),
            fg_color=Theme.SECONDARY,
            hover_color=Theme.SECONDARY_HOVER,
            text_color=Theme.SECONDARY_TEXT,
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
            self.feedback_label.configure(text="Login successful!", text_color="#10b981")
            self.on_login_success(result)
        else:
            self.feedback_label.configure(text=result, text_color=Theme.DANGER)

