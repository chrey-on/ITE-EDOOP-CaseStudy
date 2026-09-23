"""
PurrfectMatch - Staff & Admin Management Dashboard (Web / PyWebView Edition)
Full Back-Office CRUD for Shelter Staff and Administrators.
"""

import os
import sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import webview
from database.db_connection import DatabaseConnection
from models.cat import Cat
from models.adopter import Adopter
from controllers.cat_controller import CatController
from controllers.adopter_controller import AdopterController
from controllers.application_controller import ApplicationController
from controllers.auth_controller import AuthController


class AdminAPI:
    """Staff and Admin management API bridge exposed to admin.html."""
    def __init__(self):
        self.cat_ctrl = CatController()
        self.adopter_ctrl = AdopterController()
        self.app_ctrl = ApplicationController()
        self.auth_ctrl = AuthController()

    def staff_login(self, username, password):
        """Authenticates staff credentials."""
        ok, res = self.auth_ctrl.login(username, password)
        if ok:
            return {"success": True, "user": res.to_dict()}
        return {"success": False, "message": str(res)}

    # Cats CRUD
    def get_cats(self):
        cats = self.cat_ctrl.get_all_cats()
        return [cat.to_dict() for cat in cats]

    def save_cat(self, data):
        cat_id = data.get("id")
        cat = Cat(
            id=cat_id,
            name=data.get("name", ""),
            breed=data.get("breed", "Domestic Shorthair"),
            age_months=data.get("age_months", 12),
            gender=data.get("gender", "Female"),
            adoption_status=data.get("adoption_status", "Available"),
            color=data.get("color", "Mixed"),
            cage_number=data.get("cage_number", "Suite A-1"),
            notes=data.get("notes", "")
        )

        if cat_id:
            ok, msg = self.cat_ctrl.update_cat(cat)
            return {"success": ok, "message": msg}
        else:
            ok, res = self.cat_ctrl.create_cat(cat)
            return {"success": ok, "id": res if ok else None, "message": str(res)}

    def delete_cat(self, cat_id):
        ok, msg = self.cat_ctrl.delete_cat(cat_id)
        return {"success": ok, "message": msg}

    # Adopters CRUD
    def get_all_adopters(self):
        adopters = self.adopter_ctrl.get_all_adopters()
        return [a.to_dict() for a in adopters]

    def save_adopter(self, data):
        adopter_id = data.get("id")
        adopter = Adopter(
            id=adopter_id,
            full_name=data.get("full_name", ""),
            contact_number=data.get("contact_number", ""),
            email=data.get("email", ""),
            address=data.get("address", ""),
            housing_type=data.get("housing_type", "House with Yard")
        )

        if adopter_id:
            ok, msg = self.adopter_ctrl.update_adopter(adopter)
            return {"success": ok, "message": msg}
        else:
            ok, res = self.adopter_ctrl.create_adopter(adopter)
            return {"success": ok, "id": res if ok else None, "message": str(res)}

    def delete_adopter(self, adopter_id):
        ok, msg = self.adopter_ctrl.delete_adopter(adopter_id)
        return {"success": ok, "message": msg}

    # Applications CRUD & Workflow
    def get_all_applications(self):
        apps = self.app_ctrl.get_all_applications()
        return [a.to_dict() for a in apps]

    def update_application_status(self, app_id, new_status):
        ok, msg = self.app_ctrl.update_application(app_id, new_status)
        return {"success": ok, "message": msg}


def main():
    db = DatabaseConnection()
    db.initialize_database()

    api = AdminAPI()
    html_path = os.path.join(os.path.dirname(__file__), "templates", "admin.html")

    window = webview.create_window(
        title="🐾 PurrfectMatch - Staff Management Dashboard",
        url=html_path,
        js_api=api,
        width=1250,
        height=850,
        min_size=(980, 680)
    )

    webview.start(debug=False)


if __name__ == "__main__":
    main()
