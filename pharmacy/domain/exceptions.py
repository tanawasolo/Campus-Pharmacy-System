"""Exceptions for the Campus Pharmacy System.

Every rule violation in the domain model and the service layer raises a
subclass of PharmacyError. The tkinter screens catch PharmacyError and show
str(exc) in a message box, so each exception builds a readable message from
the values it is given (R14).

The names and constructor arguments are listed in docs/contract.md. Check the
contract before renaming anything or changing a signature.
"""

from __future__ import annotations

__all__ = [
    "PharmacyError",
    "InvalidPriceError",
    "InvalidReorderLevelError",
    "InvalidQuantityError",
    "InsufficientStockError",
    "UnauthorisedPrescriberError",
    "AlreadyDispensedError",
    "CancelledPrescriptionError",
    "DuplicateMedicineError",
    "EmptyPrescriptionError",
]


class PharmacyError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return self.message


class InvalidPriceError(PharmacyError):
    def __init__(self, price: object) -> None:
        super().__init__(
            f"Invalid unit price: {price!r}. Price must be greater than 0."
        )


class InvalidReorderLevelError(PharmacyError):
    def __init__(self, level: object) -> None:
        super().__init__(
            f"Invalid reorder level: {level!r}. "
        )


class InvalidQuantityError(PharmacyError):
    def __init__(
        self,
        quantity: object,
        what: str = "quantity",
        minimum: int = 1,
    ) -> None:
        self.quantity = quantity
        self.minimum = minimum
        super().__init__(
            f"Invalid {what}: {quantity!r}. "
            f"Must be a whole number of {minimum} or more."
        )


class InsufficientStockError(PharmacyError):
    def __init__(
        self,
        requested: int,
        available: int,
        medicine_code: str | None = None,
    ) -> None:
        self.requested = requested
        self.available = available
        self.medicine_code = medicine_code
        where = f" for {medicine_code}" if medicine_code else ""
        super().__init__(
            f"Insufficient stock{where}: requested {requested}, "
            f"available {available}."
        )


class UnauthorisedPrescriberError(PharmacyError):
    def __init__(
        self,
        prescriber_code: str | None,
        medicine_code: str | None = None,
    ) -> None:
        self.prescriber_code = prescriber_code
        self.medicine_code = medicine_code
        med = f" for controlled medicine {medicine_code}" if medicine_code else ""
        super().__init__(
            f"Unauthorised prescriber{med}: {prescriber_code!r} "
            "is not on the allow-list."
        )


class AlreadyDispensedError(PharmacyError):
    def __init__(self, prescription_id: object) -> None:
        self.prescription_id = prescription_id
        super().__init__(
            f"Prescription {prescription_id} has already been dispensed."
        )


class CancelledPrescriptionError(PharmacyError):
    def __init__(self, prescription_id: object, action: str = "dispense") -> None:
        self.prescription_id = prescription_id
        self.action = action
        super().__init__(
            f"Cannot {action} prescription {prescription_id}: it has been cancelled."
        )


class DuplicateMedicineError(PharmacyError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(
            f"Duplicate medicine code: {code!r} already exists."
        )


class EmptyPrescriptionError(PharmacyError):
    def __init__(self) -> None:
        super().__init__("A prescription must have at least one line.")