"""StockItem class.

A StockItem is the quantity of one medicine at one branch (R3). Two items are
equal when they have the same branch and medicine code, whatever the quantity.
The quantity has no setter: it only changes through add() and remove(), which
stop it from going below zero (R4, R5, I4). is_low() takes the reorder level as
an argument, so this class never needs to import Medicine (R11).
"""

from __future__ import annotations

from pharmacy.domain.branch import Branch
from pharmacy.domain.exceptions import (
    InsufficientStockError,
    InvalidQuantityError,
    InvalidReorderLevelError,
    PharmacyError,
)

__all__ = ["StockItem"]


class StockItem:
    def __init__(
        self,
        branch: Branch,
        medicine_code: str,
        quantity: int = 0,
    ) -> None:
        if not isinstance(branch, Branch):
            raise PharmacyError(
                f"Invalid branch: {branch!r}. Must be a Branch instance."
            )
        if not isinstance(medicine_code, str) or not medicine_code.strip():
            raise PharmacyError(
                f"Invalid medicine code: {medicine_code!r}. "
                "Code must be a non-empty string."
            )
        if (
            isinstance(quantity, bool)
            or not isinstance(quantity, int)
            or quantity < 0
        ):
            raise InvalidQuantityError(quantity, "stock quantity", minimum=0)

        self._branch = branch
        self._medicine_code = medicine_code.strip()
        self._quantity = quantity

    @property
    def branch(self) -> Branch:
        return self._branch

    @property
    def medicine_code(self) -> str:
        return self._medicine_code

    @property
    def quantity(self) -> int:
        return self._quantity

    def add(self, n: int) -> int:
        if isinstance(n, bool) or not isinstance(n, int) or n <= 0:
            raise InvalidQuantityError(n, "stock receipt")
        self._quantity += n
        return self._quantity

    def remove(self, n: int) -> int:
        if isinstance(n, bool) or not isinstance(n, int) or n <= 0:
            raise InvalidQuantityError(n, "stock removal")
        if n > self._quantity:
            raise InsufficientStockError(
                requested=n,
                available=self._quantity,
                medicine_code=self._medicine_code,
            )
        self._quantity -= n
        return self._quantity

    def is_low(self, reorder_level: int) -> bool:
        if (
            isinstance(reorder_level, bool)
            or not isinstance(reorder_level, int)
            or reorder_level < 0
        ):
            raise InvalidReorderLevelError(reorder_level)
        return self._quantity <= reorder_level

    def __repr__(self) -> str:
        return (
            f"StockItem(branch={self._branch.name!r}, "
            f"medicine_code={self._medicine_code!r}, "
            f"quantity={self._quantity})"
        )

    def __str__(self) -> str:
        return (
            f"{self._medicine_code} @ {self._branch.name}: "
            f"{self._quantity} in stock"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, StockItem):
            return NotImplemented
        return (
            self._branch == other._branch
            and self._medicine_code == other._medicine_code
        )

    def __hash__(self) -> int:
        return hash(("StockItem", self._branch, self._medicine_code))