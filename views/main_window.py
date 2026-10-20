"""
Main Window for PurrfectMatch.
Manages Sidebar Navigation, Theme Switching (Dark/Light), View Switching, and User Logout.
"""

import customtkinter as ctk
from database.db_connection import DatabaseConnection
from controllers.cat_controller import CatController
from controllers.application_controller import ApplicationController
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
            height=40,
            corner_radius=Theme.RADIUS_BTN,
            anchor="w",
            font=Theme.font_body_bold(),
            cursor="hand2",
            command=lambda: self._show_tab("cats")
        )
        self.nav_cats_btn.grid(row=4, column=0, padx=12, pady=3, sticky="ew")

        self.nav_adopters_btn = ctk.CTkButton(
            sidebar,
            text="  👥   Adopter Registry",
            height=40,
            corner_radius=Theme.RADIUS_BTN,
            anchor="w",
            font=Theme.font_body_bold(),
            cursor="hand2",
            command=lambda: self._show_tab("adopters")
        )
        self.nav_adopters_btn.grid(row=5, column=0, padx=12, pady=3, sticky="ew")

        self.nav_apps_btn = ctk.CTkButton(
            sidebar,
            text="  📋   Adoption Requests",
            height=40,
            corner_radius=Theme.RADIUS_BTN,
            anchor="w",
            font=Theme.font_body_bold(),
            cursor="hand2",
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

        # Active Database Indicator Badge
        db_type = DatabaseConnection().get_db_type()
        db_icon = "🟢" if "MySQL" in db_type else "🔵"
        self.db_status_lbl = ctk.CTkLabel(
            bottom_frame,
            text=f"{db_icon} {db_type}",
            font=Theme.font_tiny(),
            text_color=Theme.TEXT_SECONDARY,
            fg_color=Theme.BG_INPUT,
            corner_radius=Theme.RADIUS_PILL,
            height=24
        )
        self.db_status_lbl.pack(fill="x", pady=(0, 10))

        logout_btn = ctk.CTkButton(
            bottom_frame,
            text="🚪  Log Out",
            fg_color=Theme.DANGER,
            hover_color=Theme.DANGER_HOVER,
            text_color=Theme.DANGER_TEXT,
            height=38,
            corner_radius=Theme.RADIUS_BTN,
            font=Theme.font_body_bold(),
            cursor="hand2",
            command=self.on_logout
        )
        logout_btn.pack(fill="x")

        # ==========================================
        # CONTENT CONTAINER
        # ==========================================
        self.content_area = ctk.CTkFrame(self, fg_color="transparent")
        self.content_area.grid(row=0, column=1, sticky="nsew", padx=16, pady=16)
        self.content_area.grid_columnconfigure(0, weight=1)
        self.content_area.grid_rowconfigure(0, weight=0)  # KPI ribbon
        self.content_area.grid_rowconfigure(1, weight=1)  # Tab view

        # Controllers for live shelter intelligence
        self.cat_controller = CatController()
        self.app_controller = ApplicationController()

        # KPI Metrics Strip
        self.kpi_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        self.kpi_frame.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        self.kpi_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        def make_kpi_card(col, icon, title, subtitle_text, badge_bg, badge_border):
            card = ctk.CTkFrame(
                self.kpi_frame,
                corner_radius=Theme.RADIUS_CARD,
                fg_color=Theme.BG_CARD,
                border_width=1,
                border_color=Theme.BORDER
            )
            card.grid(row=0, column=col, padx=4, sticky="ew")
            card.grid_columnconfigure(1, weight=1)

            # Left Icon Chip Container
            icon_chip = ctk.CTkFrame(
                card,
                width=44,
                height=44,
                corner_radius=10,
                fg_color=badge_bg,
                border_width=1,
                border_color=badge_border
            )
            icon_chip.grid(row=0, column=0, rowspan=3, padx=(12, 10), pady=10)
            icon_chip.grid_propagate(False)

            icon_lbl = ctk.CTkLabel(
                icon_chip,
                text=icon,
                font=ctk.CTkFont(size=20)
            )
            icon_lbl.place(relx=0.5, rely=0.5, anchor="center")

            # Category Title (High contrast, bold, uppercase)
            title_lbl = ctk.CTkLabel(
                card,
                text=title.upper(),
                font=Theme.font_caption_bold(),
                text_color=Theme.TEXT_SECONDARY,
                anchor="w"
            )
            title_lbl.grid(row=0, column=1, sticky="w", pady=(8, 0))

            # Metric Value (Hero scale, bold)
            val_lbl = ctk.CTkLabel(
                card,
                text="0",
                font=Theme.font_hero(),
                text_color=Theme.TEXT_PRIMARY,
                anchor="w"
            )
            val_lbl.grid(row=1, column=1, sticky="w", pady=(0, 1))

            # Helper Subtitle
            sub_lbl = ctk.CTkLabel(
                card,
                text=subtitle_text,
                font=Theme.font_caption(),
                text_color=Theme.TEXT_MUTED,
                anchor="w"
            )
            sub_lbl.grid(row=2, column=1, sticky="w", pady=(0, 8))

            # Hover highlight
            def on_enter(e):
                card.configure(border_color=Theme.BORDER_LIGHT)
            def on_leave(e):
                card.configure(border_color=Theme.BORDER)

            for w in (card, icon_chip, icon_lbl, title_lbl, val_lbl, sub_lbl):
                w.bind("<Enter>", on_enter)
                w.bind("<Leave>", on_leave)

            return val_lbl

        self.kpi_total_lbl = make_kpi_card(
            0, "🐱", "Total Cats", "Active shelter roster",
            badge_bg=("#ede9fe", "#261b40"), badge_border=("#ddd6fe", "#432874")
        )
        self.kpi_avail_lbl = make_kpi_card(
            1, "🐾", "Available", "Ready for adoption",
            badge_bg=("#d1fae5", "#0d3326"), badge_border=("#a7f3d0", "#14532d")
        )
        self.kpi_pending_lbl = make_kpi_card(
            2, "⏳", "Pending Apps", "Awaiting staff review",
            badge_bg=("#fef3c7", "#382405"), badge_border=("#fde68a", "#78350f")
        )
        self.kpi_adopted_lbl = make_kpi_card(
            3, "💖", "Rehomed", "Forever homes found",
            badge_bg=("#fce7f3", "#3b1227"), badge_border=("#fbcfe8", "#831843")
        )

        # Views Container
        self.view_container = ctk.CTkFrame(self.content_area, fg_color="transparent")
        self.view_container.grid(row=1, column=0, sticky="nsew")
        self.view_container.grid_rowconfigure(0, weight=1)
        self.view_container.grid_columnconfigure(0, weight=1)

        # Initialize Views inside view_container
        self.cat_view = CatManagementView(self.view_container, on_data_changed=self._handle_global_data_changed)
        self.adopter_view = AdopterView(self.view_container, on_data_changed=self._handle_global_data_changed)
        self.app_view = ApplicationView(self.view_container, on_data_changed=self._handle_global_data_changed)

        self._update_kpi_metrics()

    def _update_kpi_metrics(self):
        """Fetches fresh shelter KPI totals across cats and applications."""
        try:
            cats = self.cat_controller.get_all_cats()
            total_cats = len(cats)
            avail_cats = len([c for c in cats if c.adoption_status == "Available"])
            adopted_cats = len([c for c in cats if c.adoption_status == "Adopted"])

            # Active applications only (excluding archived)
            apps = self.app_controller.get_all_applications("All Active")
            pending_apps = len([a for a in apps if a.review_status in ("Pending Review", "Interview Scheduled", "Pending")])

            self.kpi_total_lbl.configure(text=f"{total_cats} Cats")
            self.kpi_avail_lbl.configure(text=f"{avail_cats} Ready")
            self.kpi_pending_lbl.configure(text=f"{pending_apps} In-Review")
            self.kpi_adopted_lbl.configure(text=f"{adopted_cats} Rehomed")
        except Exception:
            pass

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
        self._update_kpi_metrics()

    def _change_appearance_mode(self, mode):
        ctk.set_appearance_mode(mode)
