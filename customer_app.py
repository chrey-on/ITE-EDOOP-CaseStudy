"""
PurrfectMatch - Customer Adoption Portal (Native CustomTkinter Desktop GUI)
100% Python OOP. Designed for adopters & public visitors.
Features:
- Browse cat catalog as guest.
- Centered Auth Modal appears when clicking 'Adopt Me!' as guest.
- Direct Application modal when logged in.
- Track application statuses in 'My Applications'.
"""

import customtkinter as ctk
from database.db_connection import DatabaseConnection
from views.theme import Theme
from views.customer.customer_portal_view import CustomerPortalView


class CustomerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("PurrfectMatch - Cat Adoption Portal")
        self.geometry("1120x750")
        self.minsize(980, 650)
        self._center_window(1120, 750)

        ctk.set_appearance_mode("Light")
        ctk.set_default_color_theme("blue")
        self.configure(fg_color=Theme.BG_ROOT)

        # Initialize SQLite database
        db = DatabaseConnection()
        db.initialize_database()

        # Mount Customer Portal View
        self.portal_view = CustomerPortalView(self)
        self.portal_view.pack(fill="both", expand=True)

    def _center_window(self, width, height):
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")


def main():
    app = CustomerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
