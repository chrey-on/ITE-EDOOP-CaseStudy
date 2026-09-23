"""
Adopter Model representing an applicant/adopter profile.
Demonstrates Encapsulation and Data Validation.
"""


class Adopter:
    HOUSING_CHOICES = ["Apartment", "House with Yard", "Condo", "Townhouse"]
    STATUS_CHOICES = ["Active", "Approved", "Inactive"]

    def __init__(
        self,
        id=None,
        full_name="",
        contact_number="",
        email="",
        address="",
        housing_type="House with Yard",
        has_other_pets=False,
        status="Active",
        created_at=None
    ):
        self._id = id
        self.full_name = full_name
        self.contact_number = contact_number
        self.email = email
        self.address = address
        self.housing_type = housing_type
        self.has_other_pets = bool(has_other_pets)
        self.status = status
        self._created_at = created_at

    @property
    def id(self):
        return self._id

    @property
    def full_name(self):
        return self._full_name

    @full_name.setter
    def full_name(self, value):
        val = str(value).strip()
        if not val:
            raise ValueError("Adopter name cannot be empty.")
        self._full_name = val

    @property
    def contact_number(self):
        return self._contact_number

    @contact_number.setter
    def contact_number(self, value):
        val = str(value).strip()
        if not val:
            raise ValueError("Contact number cannot be empty.")
        self._contact_number = val

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        self._email = str(value).strip()

    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, value):
        val = str(value).strip()
        if not val:
            raise ValueError("Address cannot be empty.")
        self._address = val

    @property
    def housing_type(self):
        return self._housing_type

    @housing_type.setter
    def housing_type(self, value):
        val = str(value).strip()
        self._housing_type = val if val in self.HOUSING_CHOICES else "House with Yard"

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        val = str(value).strip()
        self._status = val if val in self.STATUS_CHOICES else "Active"

    def to_dict(self):
        return {
            "id": self._id,
            "full_name": self._full_name,
            "contact_number": self._contact_number,
            "email": self._email,
            "address": self._address,
            "housing_type": self._housing_type,
            "has_other_pets": int(self.has_other_pets),
            "status": self._status,
            "created_at": str(self._created_at) if self._created_at else None
        }

    @classmethod
    def from_dict(cls, data: dict):
        if not data:
            return None
        return cls(
            id=data.get("id"),
            full_name=data.get("full_name", ""),
            contact_number=data.get("contact_number", ""),
            email=data.get("email", ""),
            address=data.get("address", ""),
            housing_type=data.get("housing_type", "House with Yard"),
            has_other_pets=bool(data.get("has_other_pets", 0)),
            status=data.get("status", "Active"),
            created_at=data.get("created_at")
        )
