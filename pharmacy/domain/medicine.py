"""Medicine classes.

Medicine is an abstract base class. It holds the shared data (code, name,
unit price, reorder level) and checks it in property setters, so a Medicine
with bad values can never be created. OrdinaryMedicine and ControlledMedicine
fill in requires_authorisation() and category(), which lets the service call
medicine.requires_authorisation() without asking what kind of medicine it is.

The database keeps a single is_controlled flag. make_medicine() turns that
flag back into the right subclass when the repository loads a row.
"""

from __future__ import annotations

import math
from abc import ABC, abstractmethod

from pharmacy.domain.exceptions import (
    InvalidPriceError,
    InvalidReorderLevelError,
    PharmacyError,
)

__all__ = [
    "Medicine",
    "OrdinaryMedicine",
    "ControlledMedicine",
    "make_medicine",
]


class Medicine(ABC):
    def __init__(
        self,
        code: str,
        name: str,
        unit_price: float,
        reorder_level: int,
    ) -> None:
        self.code = code
        self.name = name
        self.unit_price = unit_price
        self.reorder_level = reorder_level

    @property
    def code(self) -> str:
        return self._code

    @code.setter
    def code(self, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise PharmacyError(
                f"Invalid medicine code: {value!r}. "
                "Code must be a non-empty string."
            )
        self._code = value.strip()

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise PharmacyError(
                f"Invalid medicine name: {value!r}. "
                "Name must be a non-empty string."
            )
        self._name = value.strip()

    @property
    def unit_price(self) -> float:
        return self._unit_price

    @unit_price.setter
    def unit_price(self, value: float) -> None:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise InvalidPriceError(value)
        if not math.isfinite(value) or value <= 0:
            raise InvalidPriceError(value)
        self._unit_price = float(value)

    @property
    def reorder_level(self) -> int:
        return self._reorder_level

    @reorder_level.setter
    def reorder_level(self, value: int) -> None:
        if isinstance(value, bool) or not isinstance(value, int):
            raise InvalidReorderLevelError(value)
        if value < 0:
            raise InvalidReorderLevelError(value)
        self._reorder_level = value

    @abstractmethod
    def requires_authorisation(self) -> bool:
        ...

    @abstractmethod
    def category(self) -> str:
        ...

    @property
    def is_controlled(self) -> bool:
        return self.requires_authorisation()

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"code={self._code!r}, "
            f"name={self._name!r}, "
            f"unit_price={self._unit_price}, "
            f"reorder_level={self._reorder_level})"
        )


class OrdinaryMedicine(Medicine):
    def requires_authorisation(self) -> bool:
        return False

    def category(self) -> str:
        return "Ordinary"

    def __str__(self) -> str:
        return (
            f"{self.code}: {self.name} "
            f"({self.category()}, unit price {self.unit_price:.2f})"
        )


class ControlledMedicine(Medicine):
    def requires_authorisation(self) -> bool:
        return True

    def category(self) -> str:
        return "Controlled"

    def __str__(self) -> str:
        return (
            f"{self.code}: {self.name} "
            f"({self.category()}, unit price {self.unit_price:.2f})"
        )


def make_medicine(
    code: str,
    name: str,
    unit_price: float,
    reorder_level: int,
    is_controlled: bool,
) -> Medicine:
    cls = ControlledMedicine if is_controlled else OrdinaryMedicine
    return cls(code, name, unit_price, reorder_level)