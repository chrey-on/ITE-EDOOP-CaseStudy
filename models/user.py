"""
User Model for Staff and Admin authentication.
Demonstrates Encapsulation and Password Security (SHA-256).
"""

import hashlib


class User:
    def __init__(self, id=None, username="", password_hash="", full_name="", role="Staff", created_at=None):
        self._id = id
        self._username = username.strip()
        self._password_hash = password_hash
        self._full_name = full_name.strip()
        self._role = role if role in ["Admin", "Staff"] else "Staff"
        self._created_at = created_at

    @property
    def id(self):
        return self._id

    @property
    def username(self):
        return self._username

    @property
    def full_name(self):
        return self._full_name

    @property
    def role(self):
        return self._role

    @property
    def password_hash(self):
        return self._password_hash

    @staticmethod
    def hash_password(plain_password: str) -> str:
        """Hashes a plain text password using SHA-256."""
        return hashlib.sha256(plain_password.encode("utf-8")).hexdigest()

    def verify_password(self, plain_password: str) -> bool:
        """Verifies given password against stored hash."""
        return self._password_hash == self.hash_password(plain_password)

    def is_admin(self) -> bool:
        return self._role == "Admin"

    def to_dict(self):
        return {
            "id": self._id,
            "username": self._username,
            "full_name": self._full_name,
            "role": self._role,
            "created_at": str(self._created_at) if self._created_at else None
        }

    @classmethod
    def from_dict(cls, data: dict):
        if not data:
            return None
        return cls(
            id=data.get("id"),
            username=data.get("username", ""),
            password_hash=data.get("password_hash", ""),
            full_name=data.get("full_name", ""),
            role=data.get("role", "Staff"),
            created_at=data.get("created_at")
        )
