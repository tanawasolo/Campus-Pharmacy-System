"""Branch class.

A branch is a dispensing point, such as Main Campus or Satellite Clinic. The
class only checks the shape of its own data: the name must be a non-empty
string and the id must be an integer of 0 or more, or None. Unique names (R2)
are enforced by the database, and stock per branch (R3) lives in StockItem.

The id is None until the repository saves the branch. It can only be given in
the constructor, so build a saved branch as Branch(name, id=row_id).
"""

from __future__ import annotations

from pharmacy.domain.exceptions import PharmacyError

__all__ = ["Branch"]


class Branch:
    def __init__(self, name: str, id: int | None = None) -> None:
        self._id = self._validate_id(id)
        self._name = self._validate_name(name)

    @property
    def id(self) -> int | None:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = self._validate_name(value)

    @staticmethod
    def _validate_id(value: int | None) -> int | None:
        if value is None:
            return None
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise PharmacyError(
                f"Invalid branch id: {value!r}. "
                "Id must be a whole number of 0 or more, or None."
            )
        return value

    @staticmethod
    def _validate_name(value: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise PharmacyError(
                f"Invalid branch name: {value!r}. "
                "Name must be a non-empty string."
            )
        return value.strip()

    def __repr__(self) -> str:
        return f"Branch(id={self._id!r}, name={self._name!r})"

    def __str__(self) -> str:
        return self._name

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Branch):
            return NotImplemented
        if self._id is not None and other._id is not None:
            return self._id == other._id
        if self._id is None and other._id is None:
            return self._name == other._name
        return False

    def __hash__(self) -> int:
        if self._id is not None:
            return hash(("Branch", self._id))
        return hash(("Branch", None))