"""
PurrfectMatch - Staff & Admin Management Portal (Native CustomTkinter Desktop GUI)
100% Python OOP. Designed for shelter staff and administrators.
Features:
- Secure Staff/Admin Login with SHA-256 verification.
- Full CRUD for Cats, Adopters, and Adoption Applications.
- Live search, status filters, and event synchronization.
"""

from main import PurrfectMatchApp


def main():
    app = PurrfectMatchApp()
    app.mainloop()


if __name__ == "__main__":
    main()
