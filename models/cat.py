"""
Cat Model representing a shelter cat profile.
Demonstrates Encapsulation with property validation and helper formatting methods.
"""

from datetime import date


class Cat:
    STATUS_CHOICES = ["Available", "Pending", "Adopted", "Medical Hold"]
    GENDER_CHOICES = ["Male", "Female", "Unknown"]

    def __init__(
        self,
        id=None,
        name="",
        breed="Domestic Shorthair",
        age_months=12,
        gender="Unknown",
        color="Mixed",
        intake_date=None,
        health_status="Healthy",
        is_spayed_neutered=False,
        adoption_status="Available",
        cage_number="Cage A-1",
        notes="",
        created_at=None
    ):
        self._id = id
        self.name = name
        self.breed = breed
        self.age_months = age_months
        self.gender = gender
        self.color = color
        self.intake_date = intake_date or date.today().isoformat()
        self.health_status = health_status
        self.is_spayed_neutered = bool(is_spayed_neutered)
        self.adoption_status = adoption_status
        self.cage_number = cage_number
        self.notes = notes
        self._created_at = created_at

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        val = str(value).strip()
        if not val:
            raise ValueError("Cat name cannot be empty.")
        self._name = val

    @property
    def breed(self):
        return self._breed

    @breed.setter
    def breed(self, value):
        self._breed = str(value).strip() or "Domestic Shorthair"

    @property
    def age_months(self):
        return self._age_months

    @age_months.setter
    def age_months(self, value):
        try:
            val = int(value)
            if val < 0:
                raise ValueError
            self._age_months = val
        except (ValueError, TypeError):
            raise ValueError("Age must be a non-negative number of months.")

    @property
    def gender(self):
        return self._gender

    @gender.setter
    def gender(self, value):
        val = str(value).capitalize()
        self._gender = val if val in self.GENDER_CHOICES else "Unknown"

    @property
    def adoption_status(self):
        return self._adoption_status

    @adoption_status.setter
    def adoption_status(self, value):
        val = str(value).strip()
        if val not in self.STATUS_CHOICES:
            self._adoption_status = "Available"
        else:
            self._adoption_status = val

    @property
    def formatted_age(self) -> str:
        """Returns readable age string such as '1 yr 2 mos' or '7 mos'."""
        years = self._age_months // 12
        months = self._age_months % 12
        parts = []
        if years > 0:
            parts.append(f"{years} yr{'s' if years > 1 else ''}")
        if months > 0 or years == 0:
            parts.append(f"{months} mo{'s' if months > 1 else ''}")
        return " ".join(parts)

    def to_dict(self):
        return {
            "id": self._id,
            "name": self._name,
            "breed": self._breed,
            "age_months": self._age_months,
            "formatted_age": self.formatted_age,
            "gender": self._gender,
            "color": self.color,
            "intake_date": str(self.intake_date),
            "health_status": self.health_status,
            "is_spayed_neutered": int(self.is_spayed_neutered),
            "adoption_status": self._adoption_status,
            "cage_number": self.cage_number,
            "notes": self.notes
        }

    @classmethod
    def from_dict(cls, data: dict):
        if not data:
            return None
        return cls(
            id=data.get("id"),
            name=data.get("name", ""),
            breed=data.get("breed", "Domestic Shorthair"),
            age_months=data.get("age_months", 12),
            gender=data.get("gender", "Unknown"),
            color=data.get("color", "Mixed"),
            intake_date=data.get("intake_date"),
            health_status=data.get("health_status", "Healthy"),
            is_spayed_neutered=bool(data.get("is_spayed_neutered", 0)),
            adoption_status=data.get("adoption_status", "Available"),
            cage_number=data.get("cage_number", "Cage A-1"),
            notes=data.get("notes", ""),
            created_at=data.get("created_at")
        )
