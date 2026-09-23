"""
Adopter Controller managing CRUD operations and search for Adopters.
"""

from database.db_connection import DatabaseConnection
from models.adopter import Adopter


class AdopterController:
    def __init__(self):
        self.db = DatabaseConnection()

    def create_adopter(self, adopter: Adopter):
        """Inserts a new Adopter record into the database."""
        query = """
            INSERT INTO adopters (
                full_name, contact_number, email, address,
                housing_type, has_other_pets, status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            adopter.full_name,
            adopter.contact_number,
            adopter.email,
            adopter.address,
            adopter.housing_type,
            int(adopter.has_other_pets),
            adopter.status
        )
        try:
            result = self.db.execute_query(query, params)
            return True, result["lastrowid"]
        except Exception as e:
            return False, f"Failed to register adopter: {e}"

    def get_all_adopters(self):
        """Retrieves all registered adopters."""
        try:
            query = "SELECT * FROM adopters ORDER BY id DESC"
            rows = self.db.fetch_all(query)
            return [Adopter.from_dict(row) for row in rows]
        except Exception as e:
            print(f"Error fetching adopters: {e}")
            return []

    def search_adopters(self, query_text):
        """Searches adopters by name, email, or contact number."""
        try:
            query_pattern = f"%{query_text.strip()}%"
            sql = """
                SELECT * FROM adopters 
                WHERE full_name LIKE %s OR email LIKE %s OR contact_number LIKE %s
                ORDER BY id DESC
            """
            rows = self.db.fetch_all(sql, (query_pattern, query_pattern, query_pattern))
            return [Adopter.from_dict(row) for row in rows]
        except Exception as e:
            print(f"Error searching adopters: {e}")
            return []

    def get_adopter_by_id(self, adopter_id):
        """Fetches an adopter by ID."""
        try:
            row = self.db.fetch_one("SELECT * FROM adopters WHERE id = %s", (adopter_id,))
            return Adopter.from_dict(row) if row else None
        except Exception as e:
            print(f"Error finding adopter {adopter_id}: {e}")
            return None

    def update_adopter(self, adopter: Adopter):
        """Updates an existing adopter record."""
        if not adopter.id:
            return False, "Adopter ID is required for update."

        query = """
            UPDATE adopters SET
                full_name = %s,
                contact_number = %s,
                email = %s,
                address = %s,
                housing_type = %s,
                has_other_pets = %s,
                status = %s
            WHERE id = %s
        """
        params = (
            adopter.full_name,
            adopter.contact_number,
            adopter.email,
            adopter.address,
            adopter.housing_type,
            int(adopter.has_other_pets),
            adopter.status,
            adopter.id
        )
        try:
            self.db.execute_query(query, params)
            return True, "Adopter profile updated successfully."
        except Exception as e:
            return False, f"Failed to update adopter: {e}"

    def delete_adopter(self, adopter_id):
        """Deletes an adopter record by ID."""
        try:
            self.db.execute_query("DELETE FROM adopters WHERE id = %s", (adopter_id,))
            return True, "Adopter record deleted successfully."
        except Exception as e:
            return False, f"Failed to delete adopter: {e}"
