"""
PurrfectMatch: Cat Adoption & Shelter Management System
Main Application Entry Point (EDOOP Case Study)

Author: EDOOP Student Group
Language: Python 3
GUI Framework: CustomTkinter
Database: SQLite3 (100% Offline, Zero-installation)
"""

import sys
import os
from tkinter import messagebox
import customtkinter as ctk

from database.db_connection import DatabaseConnection
from views.theme import Theme
from views.login_view import LoginView
from views.main_window import MainWindow


class PurrfectMatchApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Configuration
        self.title("PurrfectMatch - Cat Adoption & Shelter Management System")
        self.geometry("1120x720")
        self.minsize(980, 620)
        self._center_window(1120, 720)

        # Apply Global CustomTkinter Theme
        ctk.set_appearance_mode("Light")
        ctk.set_default_color_theme("blue")
        self.configure(fg_color=Theme.BG_ROOT)

        # Configure Root Layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.current_frame = None

        # Check and Initialize SQLite Database
        self._init_database()

    def _center_window(self, width, height):
        """Centers the application window on screen."""
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _init_database(self):
        """Initializes database schema and seed data on SQLite."""
        db = DatabaseConnection()
        success, message = db.initialize_database()

        if not success:
            print(f"[Database Error]: {message}")
            self._show_db_error_screen(message)
        else:
            print("[Database]: SQLite database connected and initialized.")
            self.show_login()

    def _show_db_error_screen(self, error_message):
        """Renders an informative connection error screen with a retry button."""
        if self.current_frame:
            self.current_frame.destroy()

        err_frame = ctk.CTkFrame(self, corner_radius=15)
        err_frame.grid(row=0, column=0, padx=40, pady=40, sticky="nsew")
        err_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            err_frame,
            text="⚠️ Database Notice",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#e67e22"
        ).pack(pady=(40, 10))

        info_text = (
            "Could not initialize the SQLite database.\n\n"
            "Please ensure you have write permissions in the project folder,\n"
            "then click 'Retry Connection' below."
        )
        ctk.CTkLabel(
            err_frame,
            text=info_text,
            font=ctk.CTkFont(size=14),
            justify="left"
        ).pack(pady=15, padx=30)

        details_lbl = ctk.CTkLabel(
            err_frame,
            text=f"Details: {error_message}",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        details_lbl.pack(pady=10)

        retry_btn = ctk.CTkButton(
            err_frame,
            text="🔄 Retry Connection",
            width=200,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._init_database
        )
        retry_btn.pack(pady=20)

        self.current_frame = err_frame

    def show_login(self):
        """Displays the staff login screen."""
        if self.current_frame:
            self.current_frame.destroy()

        login_container = ctk.CTkFrame(self, fg_color="transparent")
        login_container.grid(row=0, column=0, sticky="nsew")
        login_container.grid_columnconfigure(0, weight=1)
        login_container.grid_rowconfigure(0, weight=1)

        self.login_view = LoginView(login_container, on_login_success=self.show_main_window)
        self.login_view.grid(row=0, column=0, padx=20, pady=20)

        self.current_frame = login_container

    def show_main_window(self, user):
        """Displays the main dashboard upon successful authentication."""
        if self.current_frame:
            self.current_frame.destroy()

        self.main_window = MainWindow(self, current_user=user, on_logout=self.show_login)
        self.main_window.grid(row=0, column=0, sticky="nsew")

        self.current_frame = self.main_window


def main():
    app = PurrfectMatchApp()
    app.mainloop()


if __name__ == "__main__":
    main()
