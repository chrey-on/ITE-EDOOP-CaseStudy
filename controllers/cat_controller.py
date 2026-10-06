"""
Cat Controller managing CRUD operations, multi-image attachments, and search/filter logic for Cats.
"""

from database.db_connection import DatabaseConnection
from models.cat import Cat
from controllers.image_service import ImageService


class CatController:
    def __init__(self):
        self.db = DatabaseConnection()

    def create_cat(self, cat: Cat):
        """Inserts a new Cat record into the database, including attached images."""
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
            new_id = result["lastrowid"]
            if cat.images:
                self.set_cat_images(new_id, cat.images)
            return True, new_id
        except Exception as e:
            return False, f"Failed to register cat: {e}"

    def get_all_cats(self, status_filter=None):
        """Retrieves all cats with their images, optionally filtered by adoption status."""
        try:
            if status_filter and status_filter != "All":
                query = "SELECT * FROM cats WHERE adoption_status = %s ORDER BY id DESC"
                rows = self.db.fetch_all(query, (status_filter,))
            else:
                query = "SELECT * FROM cats ORDER BY id DESC"
                rows = self.db.fetch_all(query)
            cats = [Cat.from_dict(row) for row in rows]
            return self._populate_images(cats)
        except Exception as e:
            print(f"Error fetching cats: {e}")
            return []

    def search_cats(self, query_text, status_filter=None):
        """Searches cats by name, breed, color, or cage number with loaded images."""
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
            cats = [Cat.from_dict(row) for row in rows]
            return self._populate_images(cats)
        except Exception as e:
            print(f"Error searching cats: {e}")
            return []

    def get_cat_by_id(self, cat_id):
        """Fetches a single cat by ID with loaded images."""
        try:
            row = self.db.fetch_one("SELECT * FROM cats WHERE id = %s", (cat_id,))
            if row:
                cat = Cat.from_dict(row)
                cat.images = self.get_cat_images(cat.id)
                return cat
            return None
        except Exception as e:
            print(f"Error finding cat {cat_id}: {e}")
            return None

    def update_cat(self, cat: Cat):
        """Updates an existing cat record and synchronizes its images."""
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
            if hasattr(cat, "images") and cat.images is not None:
                self.set_cat_images(cat.id, cat.images)
            return True, "Cat profile updated successfully."
        except Exception as e:
            return False, f"Failed to update cat: {e}"

    def delete_cat(self, cat_id):
        """Deletes a cat record and cleans up associated image files and database entries."""
        try:
            # Delete physical image files
            images = self.get_cat_images(cat_id)
            for img_path in images:
                ImageService.delete_image_file(img_path)

            self.db.execute_query("DELETE FROM cat_images WHERE cat_id = %s", (cat_id,))
            self.db.execute_query("DELETE FROM cats WHERE id = %s", (cat_id,))
            return True, "Cat profile deleted successfully."
        except Exception as e:
            return False, f"Failed to delete cat: {e}"

    def get_available_cats(self):
        """Returns cats currently available for adoption."""
        return self.get_all_cats(status_filter="Available")

    # ==========================================
    # IMAGE MANAGEMENT (Up to 10 images per cat)
    # ==========================================
    def get_cat_images(self, cat_id: int) -> list:
        """Retrieves list of image relative paths for a cat in order, verifying files exist on disk."""
        try:
            rows = self.db.fetch_all(
                "SELECT id, image_path FROM cat_images WHERE cat_id = %s ORDER BY is_primary DESC, id ASC",
                (cat_id,)
            )
            import os
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            valid_paths = []
            for r in rows:
                p = r["image_path"]
                full = p if os.path.isabs(p) else os.path.join(base_dir, p)
                if os.path.isfile(full):
                    valid_paths.append(p)
            return valid_paths
        except Exception as e:
            print(f"Error fetching images for cat {cat_id}: {e}")
            return []

    def set_cat_images(self, cat_id: int, image_paths: list) -> bool:
        """
        Updates the cat's image list (up to 10 images).
        Deletes files that are no longer referenced, and inserts new records.
        """
        try:
            # Clamp to max 10
            clamped = list(image_paths)[:10]

            current_rows = self.db.fetch_all("SELECT id, image_path FROM cat_images WHERE cat_id = %s", (cat_id,))
            current_paths = [r["image_path"] for r in current_rows]

            # Remove old unreferenced images
            for r in current_rows:
                if r["image_path"] not in clamped:
                    self.db.execute_query("DELETE FROM cat_images WHERE id = %s", (r["id"],))
                    ImageService.delete_image_file(r["image_path"])

            # Insert or update
            for idx, p in enumerate(clamped):
                is_primary = 1 if idx == 0 else 0
                if p not in current_paths:
                    self.db.execute_query(
                        "INSERT INTO cat_images (cat_id, image_path, is_primary) VALUES (%s, %s, %s)",
                        (cat_id, p, is_primary)
                    )
                else:
                    self.db.execute_query(
                        "UPDATE cat_images SET is_primary = %s WHERE cat_id = %s AND image_path = %s",
                        (is_primary, cat_id, p)
                    )
            return True
        except Exception as e:
            print(f"Error setting images for cat {cat_id}: {e}")
            return False

    def _populate_images(self, cats: list) -> list:
        """Populates the images list on each Cat model instance."""
        for cat in cats:
            cat.images = self.get_cat_images(cat.id)
        return cats
