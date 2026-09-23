"""
PurrfectMatch - Customer Adoption Portal (Web / PyWebView Edition)
100% Customer & Adopter Facing. No staff login or management controls.
"""

import os
import sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import webview
from database.db_connection import DatabaseConnection
from models.adopter import Adopter
from models.application import AdoptionApplication
from controllers.cat_controller import CatController
from controllers.adopter_controller import AdopterController
from controllers.application_controller import ApplicationController


class CustomerAPI:
    """Customer-facing API bridge exposed to customer.html."""
    def __init__(self):
        self.cat_ctrl = CatController()
        self.adopter_ctrl = AdopterController()
        self.app_ctrl = ApplicationController()

    def get_cats(self):
        """Returns all cats for the public catalog."""
        cats = self.cat_ctrl.get_all_cats()
        return [cat.to_dict() for cat in cats]

    def find_adopter_by_contact(self, contact_or_email):
        """Finds an existing adopter profile by contact number or email."""
        results = self.adopter_ctrl.search_adopters(contact_or_email)
        if results:
            return results[0].to_dict()
        return None

    def register_adopter(self, data):
        """Registers a new adopter profile."""
        try:
            adopter = Adopter(
                full_name=data.get("full_name", ""),
                contact_number=data.get("contact_number", ""),
                email=data.get("email", ""),
                address=data.get("address", ""),
                housing_type=data.get("housing_type", "House with Yard")
            )
            success, res = self.adopter_ctrl.create_adopter(adopter)
            if success:
                return {"success": True, "id": res}
            else:
                return {"success": False, "message": str(res)}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def submit_application(self, data):
        """Submits an adoption application from an adopter."""
        try:
            app = AdoptionApplication(
                cat_id=data.get("cat_id"),
                adopter_id=data.get("adopter_id"),
                notes=data.get("notes", "")
            )
            success, res = self.app_ctrl.create_application(app)
            if success:
                return {"success": True, "id": res}
            else:
                return {"success": False, "message": str(res)}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def get_my_applications(self, adopter_id):
        """Retrieves applications filed by a specific adopter."""
        all_apps = self.app_ctrl.get_all_applications()
        return [a.to_dict() for a in all_apps if a.adopter_id == adopter_id]


def main():
    db = DatabaseConnection()
    db.initialize_database()

    api = CustomerAPI()
    html_path = os.path.join(os.path.dirname(__file__), "templates", "customer.html")

    window = webview.create_window(
        title="🐾 PurrfectMatch - Cat Adoption Portal",
        url=html_path,
        js_api=api,
        width=1200,
        height=820,
        min_size=(950, 650)
    )

    webview.start(debug=False)


if __name__ == "__main__":
    main()
