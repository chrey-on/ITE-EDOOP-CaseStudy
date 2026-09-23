"""
AdoptionApplication Model representing an application linking an Adopter to a Cat.
Demonstrates Relational OOP entity modelling and lifecycle status tracking.
"""

from datetime import date


class AdoptionApplication:
    STATUS_CHOICES = [
        "Pending Review",
        "Interview Scheduled",
        "Approved",
        "Rejected",
        "Completed"
    ]

    def __init__(
        self,
        id=None,
        cat_id=None,
        adopter_id=None,
        application_date=None,
        review_status="Pending Review",
        notes="",
        cat_name="",
        adopter_name="",
        created_at=None,
        updated_at=None
    ):
        self._id = id
        self.cat_id = cat_id
        self.adopter_id = adopter_id
        self.application_date = application_date or date.today().isoformat()
        self.review_status = review_status
        self.notes = notes
        self.cat_name = cat_name
        self.adopter_name = adopter_name
        self._created_at = created_at
        self._updated_at = updated_at

    @property
    def id(self):
        return self._id

    @property
    def review_status(self):
        return self._review_status

    @review_status.setter
    def review_status(self, value):
        val = str(value).strip()
        if val not in self.STATUS_CHOICES:
            self._review_status = "Pending Review"
        else:
            self._review_status = val

    def to_dict(self):
        return {
            "id": self._id,
            "cat_id": self.cat_id,
            "adopter_id": self.adopter_id,
            "application_date": str(self.application_date),
            "review_status": self._review_status,
            "notes": self.notes,
            "cat_name": self.cat_name,
            "adopter_name": self.adopter_name,
            "created_at": str(self._created_at) if self._created_at else None,
            "updated_at": str(self._updated_at) if self._updated_at else None
        }

    @classmethod
    def from_dict(cls, data: dict):
        if not data:
            return None
        return cls(
            id=data.get("id"),
            cat_id=data.get("cat_id"),
            adopter_id=data.get("adopter_id"),
            application_date=data.get("application_date"),
            review_status=data.get("review_status", "Pending Review"),
            notes=data.get("notes", ""),
            cat_name=data.get("cat_name", ""),
            adopter_name=data.get("adopter_name", ""),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )
