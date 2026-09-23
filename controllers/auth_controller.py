"""
Authentication Controller managing user session and login validation.
"""

from database.db_connection import DatabaseConnection
from models.user import User


class AuthController:
    _instance = None
    _current_user = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AuthController, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.db = DatabaseConnection()

    def login(self, username, password):
        """
        Authenticates user with username and plain-text password.
        Returns (True, user_object) if successful, or (False, error_message).
        """
        username = str(username).strip()
        if not username or not password:
            return False, "Username and password are required."

        query = "SELECT * FROM users WHERE username = %s LIMIT 1"
        try:
            row = self.db.fetch_one(query, (username,))
            if not row:
                return False, "Invalid username or password."

            user = User.from_dict(row)
            if user.verify_password(password):
                AuthController._current_user = user
                return True, user
            else:
                return False, "Invalid username or password."
        except Exception as e:
            return False, f"Database authentication error: {e}"

    def logout(self):
        """Clears the active user session."""
        AuthController._current_user = None

    @classmethod
    def get_current_user(cls):
        """Returns the logged-in User instance or None."""
        return cls._current_user

    @classmethod
    def is_logged_in(cls):
        return cls._current_user is not None
