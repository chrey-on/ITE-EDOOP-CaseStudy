"""
Main Window for PurrfectMatch.
Manages Sidebar Navigation, Theme Switching (Dark/Light), View Switching, and User Logout.
"""

import customtkinter as ctk
from views.theme import Theme
from views.cat_management_view import CatManagementView
from views.adopter_view import AdopterView
from views.application_view import ApplicationView


class MainWindow(ctk.CTkFrame):
    def __init__(self, master, current_user, on_logout):
        super().__init__(master, fg_color=Theme.BG_ROOT)
        self.master = master
        self.current_user = current_user
        self.on_logout = on_logout

        self.current_tab = "cats"
        self._build_ui()
        self._show_tab("cats")

    def _build_ui(self):
        # Configure layout: Column 0 = Sidebar, Column 1 = Content
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ==========================================
        # SIDEBAR
        # ==========================================
        sidebar = ctk.CTkFrame(
            self,
            width=240,
            corner_radius=0,
            fg_color=Theme.BG_SIDEBAR,
            border_width=1,
            border_color=Theme.BORDER
        )
        sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        sidebar.grid_rowconfigure(7, weight=1)  # Spacer pushes bottom controls down

        # App Brand Header
        brand_row = ctk.CTkFrame(sidebar, fg_color="transparent")
        brand_row.grid(row=0, column=0, padx=18, pady=(20, 2), sticky="ew")

        brand_lbl = ctk.CTkLabel(
            brand_row,
            text="🐾 PurrfectMatch",
            font=Theme.font_title(),
            text_color=Theme.TEXT_PRIMARY
        )
        brand_lbl.pack(side="left")

        portal_badge = ctk.CTkLabel(
            brand_row,
            text=" ADMIN ",
            font=Theme.font_tiny(),
            fg_color=Theme.PRIMARY,
            text_color=Theme.PRIMARY_TEXT,
            corner_radius=Theme.RADIUS_PILL
        )
        portal_badge.pack(side="left", padx=(8, 0))

        sub_lbl = ctk.CTkLabel(
            sidebar,
            text="Shelter Operations Portal",
            font=Theme.font_caption(),
            text_color=Theme.TEXT_MUTED
        )
        sub_lbl.grid(row=1, column=0, padx=18, pady=(0, 16), sticky="w")

        # User Info Badge
        user_badge = ctk.CTkFrame(
            sidebar,
            fg_color=Theme.BG_CARD,
            corner_radius=Theme.RADIUS_CARD,
            border_width=1,
            border_color=Theme.BORDER
        )
        user_badge.grid(row=2, column=0, padx=14, pady=(0, 18), sticky="ew")

        user_name = self.current_user.full_name if self.current_user else "Shelter Staff"
        user_role = self.current_user.role if self.current_user else "Staff"

        ctk.CTkLabel(
            user_badge,
            text=f"👤 {user_name}",
            font=Theme.font_body_bold(),
            text_color=Theme.TEXT_PRIMARY,
            anchor="w"
        ).pack(anchor="w", padx=12, pady=(10, 2))

        role_row = ctk.CTkFrame(user_badge, fg_color="transparent")
        role_row.pack(anchor="w", padx=12, pady=(0, 10), fill="x")

        ctk.CTkLabel(
            role_row,
            text=f"Role: {user_role}",
            font=Theme.font_caption(),
            text_color=Theme.TEXT_MUTED,
            anchor="w"
        ).pack(side="left")

        role_pill = ctk.CTkLabel(
            role_row,
            text="● ONLINE",
            font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"),
            text_color=Theme.SUCCESS[0]
        )
        role_pill.pack(side="left", padx=(8, 0))

        # Navigation Section Label
        ctk.CTkLabel(
            sidebar,
            text="MANAGEMENT",
            font=Theme.font_tiny(),
            text_color=Theme.TEXT_MUTED,
            anchor="w"
        ).grid(row=3, column=0, padx=18, pady=(0, 8), sticky="w")

        # Navigation Buttons
        self.nav_cats_btn = ctk.CTkButton(
            sidebar,
            text="  🐱   Shelter Cats",
            height=38,
            corner_radius=Theme.RADIUS_BTN,
            anchor="w",
            font=Theme.font_body_bold(),
            command=lambda: self._show_tab("cats")
        )
        self.nav_cats_btn.grid(row=4, column=0, padx=12, pady=3, sticky="ew")

        self.nav_adopters_btn = ctk.CTkButton(
            sidebar,
            text="  👥   Adopter Registry",
            height=38,
            corner_radius=Theme.RADIUS_BTN,
            anchor="w",
            font=Theme.font_body_bold(),
            command=lambda: self._show_tab("adopters")
        )
        self.nav_adopters_btn.grid(row=5, column=0, padx=12, pady=3, sticky="ew")

        self.nav_apps_btn = ctk.CTkButton(
            sidebar,
            text="  📋   Adoption Requests",
            height=38,
            corner_radius=Theme.RADIUS_BTN,
            anchor="w",
            font=Theme.font_body_bold(),
            command=lambda: self._show_tab("applications")
        )
        self.nav_apps_btn.grid(row=6, column=0, padx=12, pady=3, sticky="ew")

        # Divider above bottom section
        ctk.CTkFrame(sidebar, height=1, fg_color=Theme.BORDER).grid(
            row=8, column=0, padx=14, pady=(8, 12), sticky="ew"
        )

        # Bottom Area: Appearance Mode & Logout
        bottom_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        bottom_frame.grid(row=9, column=0, padx=14, pady=(0, 18), sticky="ew")

        ctk.CTkLabel(
            bottom_frame,
            text="Appearance Mode:",
            font=Theme.font_caption_bold(),
            text_color=Theme.TEXT_MUTED,
            anchor="w"
        ).pack(anchor="w", pady=(0, 4))

        self.theme_menu = ctk.CTkOptionMenu(
            bottom_frame,
            values=["Light", "Dark", "System"],
            height=32,
            corner_radius=Theme.RADIUS_INPUT,
            fg_color=Theme.BG_INPUT,
            button_color=Theme.BG_CARD_HOVER,
            button_hover_color=Theme.BORDER_LIGHT,
            text_color=Theme.TEXT_PRIMARY,
            dropdown_fg_color=Theme.BG_CARD,
            dropdown_hover_color=Theme.BG_CARD_HOVER,
            dropdown_text_color=Theme.TEXT_PRIMARY,
            command=self._change_appearance_mode
        )
        self.theme_menu.set("Light")
        self.theme_menu.pack(fill="x", pady=(0, 10))

        logout_btn = ctk.CTkButton(
            bottom_frame,
            text="🚪  Log Out",
            fg_color=Theme.DANGER,
            hover_color=Theme.DANGER_HOVER,
            text_color=Theme.DANGER_TEXT,
            height=36,
            corner_radius=Theme.RADIUS_BTN,
            font=Theme.font_body_bold(),
            command=self.on_logout
        )
        logout_btn.pack(fill="x")

        # ==========================================
        # CONTENT CONTAINER
        # ==========================================
        self.content_area = ctk.CTkFrame(self, fg_color="transparent")
        self.content_area.grid(row=0, column=1, sticky="nsew", padx=16, pady=16)
        self.content_area.grid_columnconfigure(0, weight=1)
        self.content_area.grid_rowconfigure(0, weight=1)

        # Initialize Views
        self.cat_view = CatManagementView(self.content_area, on_data_changed=self._handle_global_data_changed)
        self.adopter_view = AdopterView(self.content_area, on_data_changed=self._handle_global_data_changed)
        self.app_view = ApplicationView(self.content_area, on_data_changed=self._handle_global_data_changed)

    def _update_nav_buttons(self, active_tab):
        nav_map = {
            "cats": self.nav_cats_btn,
            "adopters": self.nav_adopters_btn,
            "applications": self.nav_apps_btn,
        }
        for tab_name, btn in nav_map.items():
            if tab_name == active_tab:
                btn.configure(
                    fg_color=Theme.PRIMARY,
                    hover_color=Theme.PRIMARY_HOVER,
                    text_color=Theme.PRIMARY_TEXT
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    hover_color=Theme.BG_CARD_HOVER,
                    text_color=Theme.TEXT_SECONDARY
                )

    def _show_tab(self, tab_name):
        self.current_tab = tab_name

        # Hide all views
        self.cat_view.grid_forget()
        self.adopter_view.grid_forget()
        self.app_view.grid_forget()

        # Update button visual states
        self._update_nav_buttons(tab_name)

        # Show selected view
        if tab_name == "cats":
            self.cat_view.grid(row=0, column=0, sticky="nsew")
            self.cat_view.refresh_cat_list()
        elif tab_name == "adopters":
            self.adopter_view.grid(row=0, column=0, sticky="nsew")
            self.adopter_view.refresh_adopter_list()
        elif tab_name == "applications":
            self.app_view.grid(row=0, column=0, sticky="nsew")
            self.app_view.refresh_all()

    def _handle_global_data_changed(self):
        """Called when any view makes a mutation, ensuring cross-view freshness."""
        self.cat_view.refresh_cat_list()
        self.adopter_view.refresh_adopter_list()
        self.app_view.refresh_all()

    def _change_appearance_mode(self, mode):
        ctk.set_appearance_mode(mode)
