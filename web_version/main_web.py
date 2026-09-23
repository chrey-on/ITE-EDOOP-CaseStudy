"""
PurrfectMatch - Web / PyWebView Edition Launcher
Allows launching either the Customer Adoption Portal or the Staff Management Dashboard.
"""

import sys
import os

def main():
    print("=" * 60)
    print("🐾 PurrfectMatch - Web / PyWebView Edition (Option A)")
    print("=" * 60)
    print("Select which interface to launch:")
    print("  [1] 🐱 Customer Adoption Portal (customer_web.py)")
    print("  [2] 🔐 Staff & Admin Dashboard  (admin_web.py)")
    print("=" * 60)

    choice = input("Enter choice (1 or 2) [default: 1]: ").strip()
    if choice == "2":
        from web_version.admin_web import main as run_admin
        run_admin()
    else:
        from web_version.customer_web import main as run_customer
        run_customer()

if __name__ == "__main__":
    main()
