"""
Main Window for PurrfectMatch.
Manages Sidebar Navigation, Theme Switching (Dark/Light), View Switching, and User Logout.
"""

import customtkinter as ctk
from views.cat_management_view import CatManagementView
from views.adopter_view import AdopterView
from views.application_view import ApplicationView


class MainWindow(ctk.CTkFrame):
    def __init__(self, master, current_user, on_logout):
        super().__init__(master, fg_color="transparent")
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
        sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        sidebar.grid_rowconfigure(5, weight=1)  # Spacer pushes bottom controls down

        # App Brand Header
        brand_lbl = ctk.CTkLabel(
            sidebar,
            text="🐾 PurrfectMatch",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        brand_lbl.grid(row=0, column=0, padx=20, pady=(20, 2))

        sub_lbl = ctk.CTkLabel(
            sidebar,
            text="Cat Shelter Management",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        sub_lbl.grid(row=1, column=0, padx=20, pady=(0, 15))

        # User Info Badge
        user_badge = ctk.CTkFrame(sidebar, fg_color=("gray85", "gray25"), corner_radius=8)
        user_badge.grid(row=2, column=0, padx=15, pady=(0, 20), sticky="ew")

        user_name = self.current_user.full_name if self.current_user else "Shelter Staff"
        user_role = self.current_user.role if self.current_user else "Staff"

        ctk.CTkLabel(
            user_badge,
            text=f"👤 {user_name}",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", padx=10, pady=(6, 1))

        ctk.CTkLabel(
            user_badge,
            text=f"Role: {user_role}",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        ).pack(anchor="w", padx=10, pady=(0, 6))

        # Navigation Buttons
        self.nav_cats_btn = ctk.CTkButton(
            sidebar,
            text="🐱 Shelter Cats",
            height=38,
            anchor="w",
            font=ctk.CTkFont(size=13),
            command=lambda: self._show_tab("cats")
        )
        self.nav_cats_btn.grid(row=3, column=0, padx=15, pady=5, sticky="ew")

        self.nav_adopters_btn = ctk.CTkButton(
            sidebar,
            text="👤 Adopter Registry",
            height=38,
            anchor="w",
            font=ctk.CTkFont(size=13),
            command=lambda: self._show_tab("adopters")
        )
        self.nav_adopters_btn.grid(row=4, column=0, padx=15, pady=5, sticky="ew")

        self.nav_apps_btn = ctk.CTkButton(
            sidebar,
            text="📋 Adoption Requests",
            height=38,
            anchor="w",
            font=ctk.CTkFont(size=13),
            command=lambda: self._show_tab("applications")
        )
        self.nav_apps_btn.grid(row=5, column=0, padx=15, pady=5, sticky="ew")

        # Bottom Area: Appearance Mode & Logout
        bottom_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        bottom_frame.grid(row=6, column=0, padx=15, pady=(0, 20), sticky="ew")

        ctk.CTkLabel(bottom_frame, text="Appearance Mode:", font=ctk.CTkFont(size=11)).pack(anchor="w", pady=(0, 2))
        self.theme_menu = ctk.CTkOptionMenu(
            bottom_frame,
            values=["Dark", "Light", "System"],
            command=self._change_appearance_mode
        )
        self.theme_menu.pack(fill="x", pady=(0, 10))

        logout_btn = ctk.CTkButton(
            bottom_frame,
            text="🚪 Log Out",
            fg_color="#c0392b",
            hover_color="#962d22",
            height=34,
            command=self.on_logout
        )
        logout_btn.pack(fill="x")

        # ==========================================
        # CONTENT CONTAINER
        # ==========================================
        self.content_area = ctk.CTkFrame(self, fg_color="transparent")
        self.content_area.grid(row=0, column=1, sticky="nsew", padx=15, pady=15)
        self.content_area.grid_columnconfigure(0, weight=1)
        self.content_area.grid_rowconfigure(0, weight=1)

        # Initialize Views
        self.cat_view = CatManagementView(self.content_area, on_data_changed=self._handle_global_data_changed)
        self.adopter_view = AdopterView(self.content_area, on_data_changed=self._handle_global_data_changed)
        self.app_view = ApplicationView(self.content_area, on_data_changed=self._handle_global_data_changed)

    def _show_tab(self, tab_name):
        self.current_tab = tab_name

        # Hide all views
        self.cat_view.grid_forget()
        self.adopter_view.grid_forget()
        self.app_view.grid_forget()

        # Reset button styles
        default_color = ("gray85", "gray25")
        active_color = ("#3b8ed0", "#1f6aa5")

        self.nav_cats_btn.configure(fg_color=default_color if tab_name != "cats" else active_color)
        self.nav_adopters_btn.configure(fg_color=default_color if tab_name != "adopters" else active_color)
        self.nav_apps_btn.configure(fg_color=default_color if tab_name != "applications" else active_color)

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
