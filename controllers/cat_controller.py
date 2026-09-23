"""
Cat Controller managing CRUD operations and search/filter logic for Cats.
"""

from database.db_connection import DatabaseConnection
from models.cat import Cat


class CatController:
    def __init__(self):
        self.db = DatabaseConnection()

    def create_cat(self, cat: Cat):
        """Inserts a new Cat record into the database."""
        query = """
            INSERT INTO cats (
                name, breed, age_months, gender, color, intake_date,
                health_status, is_spayed_neutered, adoption_status,
                cage_number, notes
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            cat.name,
            cat.breed,
            cat.age_months,
            cat.gender,
            cat.color,
            cat.intake_date,
            cat.health_status,
            int(cat.is_spayed_neutered),
            cat.adoption_status,
            cat.cage_number,
            cat.notes
        )
        try:
            result = self.db.execute_query(query, params)
            return True, result["lastrowid"]
        except Exception as e:
            return False, f"Failed to register cat: {e}"

    def get_all_cats(self, status_filter=None):
        """Retrieves all cats, optionally filtered by adoption status."""
        try:
            if status_filter and status_filter != "All":
                query = "SELECT * FROM cats WHERE adoption_status = %s ORDER BY id DESC"
                rows = self.db.fetch_all(query, (status_filter,))
            else:
                query = "SELECT * FROM cats ORDER BY id DESC"
                rows = self.db.fetch_all(query)
            return [Cat.from_dict(row) for row in rows]
        except Exception as e:
            print(f"Error fetching cats: {e}")
            return []

    def search_cats(self, query_text, status_filter=None):
        """Searches cats by name, breed, color, or cage number."""
        try:
            query_pattern = f"%{query_text.strip()}%"
            if status_filter and status_filter != "All":
                sql = """
                    SELECT * FROM cats 
                    WHERE adoption_status = %s 
                      AND (name LIKE %s OR breed LIKE %s OR color LIKE %s OR cage_number LIKE %s)
                    ORDER BY id DESC
                """
                rows = self.db.fetch_all(sql, (status_filter, query_pattern, query_pattern, query_pattern, query_pattern))
            else:
                sql = """
                    SELECT * FROM cats 
                    WHERE name LIKE %s OR breed LIKE %s OR color LIKE %s OR cage_number LIKE %s
                    ORDER BY id DESC
                """
                rows = self.db.fetch_all(sql, (query_pattern, query_pattern, query_pattern, query_pattern))
            return [Cat.from_dict(row) for row in rows]
        except Exception as e:
            print(f"Error searching cats: {e}")
            return []

    def get_cat_by_id(self, cat_id):
        """Fetches a single cat by ID."""
        try:
            row = self.db.fetch_one("SELECT * FROM cats WHERE id = %s", (cat_id,))
            return Cat.from_dict(row) if row else None
        except Exception as e:
            print(f"Error finding cat {cat_id}: {e}")
            return None

    def update_cat(self, cat: Cat):
        """Updates an existing cat record."""
        if not cat.id:
            return False, "Cat ID is required for update."

        query = """
            UPDATE cats SET
                name = %s,
                breed = %s,
                age_months = %s,
                gender = %s,
                color = %s,
                intake_date = %s,
                health_status = %s,
                is_spayed_neutered = %s,
                adoption_status = %s,
                cage_number = %s,
                notes = %s
            WHERE id = %s
        """
        params = (
            cat.name,
            cat.breed,
            cat.age_months,
            cat.gender,
            cat.color,
            cat.intake_date,
            cat.health_status,
            int(cat.is_spayed_neutered),
            cat.adoption_status,
            cat.cage_number,
            cat.notes,
            cat.id
        )
        try:
            self.db.execute_query(query, params)
            return True, "Cat profile updated successfully."
        except Exception as e:
            return False, f"Failed to update cat: {e}"

    def delete_cat(self, cat_id):
        """Deletes a cat record by ID."""
        try:
            self.db.execute_query("DELETE FROM cats WHERE id = %s", (cat_id,))
            return True, "Cat profile deleted successfully."
        except Exception as e:
            return False, f"Failed to delete cat: {e}"

    def get_available_cats(self):
        """Returns cats currently available for adoption."""
        return self.get_all_cats(status_filter="Available")
