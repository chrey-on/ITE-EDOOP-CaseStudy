"""
Application Controller managing Adoption Applications and Status Synchronization.
Demonstrates Event-Driven business logic (e.g. auto-updating cat adoption status).
"""

from database.db_connection import DatabaseConnection
from models.application import AdoptionApplication


class ApplicationController:
    def __init__(self):
        self.db = DatabaseConnection()

    def create_application(self, app: AdoptionApplication):
        """
        Creates a new adoption application and marks the cat as 'Pending' if currently 'Available'.
        """
        query = """
            INSERT INTO adoption_applications (
                cat_id, adopter_id, application_date, review_status, notes
            ) VALUES (%s, %s, %s, %s, %s)
        """
        params = (
            app.cat_id,
            app.adopter_id,
            app.application_date,
            app.review_status,
            app.notes
        )
        try:
            result = self.db.execute_query(query, params)
            app_id = result["lastrowid"]

            # Event Trigger: If cat is Available, mark as Pending
            self.db.execute_query(
                "UPDATE cats SET adoption_status = 'Pending' WHERE id = %s AND adoption_status = 'Available'",
                (app.cat_id,)
            )

            return True, app_id
        except Exception as e:
            return False, f"Failed to submit application: {e}"

    def get_all_applications(self, status_filter=None):
        """
        Retrieves applications with joined Cat name and Adopter name.
        """
        try:
            base_sql = """
                SELECT 
                    a.id, a.cat_id, a.adopter_id, a.application_date, 
                    a.review_status, a.notes, a.created_at, a.updated_at,
                    c.name AS cat_name,
                    ad.full_name AS adopter_name
                FROM adoption_applications a
                JOIN cats c ON a.cat_id = c.id
                JOIN adopters ad ON a.adopter_id = ad.id
            """
            if status_filter and status_filter != "All":
                sql = base_sql + " WHERE a.review_status = %s ORDER BY a.id DESC"
                rows = self.db.fetch_all(sql, (status_filter,))
            else:
                sql = base_sql + " ORDER BY a.id DESC"
                rows = self.db.fetch_all(sql)

            return [AdoptionApplication.from_dict(row) for row in rows]
        except Exception as e:
            print(f"Error fetching applications: {e}")
            return []

    def search_applications(self, query_text, status_filter=None):
        """Searches applications by cat name or adopter name."""
        try:
            query_pattern = f"%{query_text.strip()}%"
            base_sql = """
                SELECT 
                    a.id, a.cat_id, a.adopter_id, a.application_date, 
                    a.review_status, a.notes, a.created_at, a.updated_at,
                    c.name AS cat_name,
                    ad.full_name AS adopter_name
                FROM adoption_applications a
                JOIN cats c ON a.cat_id = c.id
                JOIN adopters ad ON a.adopter_id = ad.id
                WHERE (c.name LIKE %s OR ad.full_name LIKE %s)
            """
            if status_filter and status_filter != "All":
                sql = base_sql + " AND a.review_status = %s ORDER BY a.id DESC"
                rows = self.db.fetch_all(sql, (query_pattern, query_pattern, status_filter))
            else:
                sql = base_sql + " ORDER BY a.id DESC"
                rows = self.db.fetch_all(sql, (query_pattern, query_pattern))

            return [AdoptionApplication.from_dict(row) for row in rows]
        except Exception as e:
            print(f"Error searching applications: {e}")
            return []

    def update_application(self, app_id, new_status, notes=None):
        """
        Updates application status and synchronizes the associated Cat's status.
        Event-Driven Actions:
        - If new_status == 'Completed': Cat status -> 'Adopted'
        - If new_status == 'Rejected': If no other active applications, Cat status -> 'Available'
        - If new_status in ('Pending Review', 'Interview Scheduled', 'Approved'): Cat status -> 'Pending'
        """
        try:
            # 1. Fetch current application to know the linked cat_id
            app_row = self.db.fetch_one(
                "SELECT cat_id, review_status FROM adoption_applications WHERE id = %s",
                (app_id,)
            )
            if not app_row:
                return False, "Application record not found."

            cat_id = app_row["cat_id"]

            # 2. Update the application
            if notes is not None:
                self.db.execute_query(
                    "UPDATE adoption_applications SET review_status = %s, notes = %s WHERE id = %s",
                    (new_status, notes, app_id)
                )
            else:
                self.db.execute_query(
                    "UPDATE adoption_applications SET review_status = %s WHERE id = %s",
                    (new_status, app_id)
                )

            # 3. Trigger Cat Status Synchronization Event
            if new_status == "Completed":
                self.db.execute_query("UPDATE cats SET adoption_status = 'Adopted' WHERE id = %s", (cat_id,))
            elif new_status == "Rejected":
                # Check if there are other pending/approved applications for this cat
                other_apps = self.db.fetch_all(
                    "SELECT id FROM adoption_applications WHERE cat_id = %s AND id != %s AND review_status IN ('Pending Review', 'Interview Scheduled', 'Approved')",
                    (cat_id, app_id)
                )
                if not other_apps:
                    self.db.execute_query("UPDATE cats SET adoption_status = 'Available' WHERE id = %s", (cat_id,))
            elif new_status in ["Pending Review", "Interview Scheduled", "Approved"]:
                self.db.execute_query("UPDATE cats SET adoption_status = 'Pending' WHERE id = %s AND adoption_status = 'Available'", (cat_id,))

            return True, "Application status updated and cat status synchronized."
        except Exception as e:
            return False, f"Failed to update application: {e}"

    def delete_application(self, app_id):
        """Deletes an application record."""
        try:
            self.db.execute_query("DELETE FROM adoption_applications WHERE id = %s", (app_id,))
            return True, "Application record deleted successfully."
        except Exception as e:
            return False, f"Failed to delete application: {e}"
