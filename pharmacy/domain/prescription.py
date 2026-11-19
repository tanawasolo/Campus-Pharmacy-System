"""Prescription and PrescriptionLine classes.

A PrescriptionLine is one medicine code and a quantity above 0 (R6, I5). A
Prescription holds the patient id, the branch, the prescriber code, its lines
and a status of pending, dispensed or cancelled (I6). The status has no setter.
It only changes through mark_dispensed() and cancel(), which allow pending to
dispensed or cancelled and nothing else (I7, I8, R9, R10).

The prescriber code is stored as given and not checked against the allow-list
here. That check happens when a controlled medicine is dispensed (R7, I9).

A prescription needs at least one line (R15). The constructor allows none so
lines can be added one at a time, and validate() raises EmptyPrescriptionError
when there are none. The database cannot express this rule, so it is Python only.
"""

from __future__ import annotations

from pharmacy.domain.branch import Branch
from pharmacy.domain.exceptions import (
    AlreadyDispensedError,
    CancelledPrescriptionError,
    EmptyPrescriptionError,
    InvalidQuantityError,
    PharmacyError,
)

__all__ = [
    "PENDING",
    "DISPENSED",
    "CANCELLED",
    "PrescriptionLine",
    "Prescription",
]

PENDING = "pending"
DISPENSED = "dispensed"
CANCELLED = "cancelled"
_VALID_STATUSES = frozenset({PENDING, DISPENSED, CANCELLED})


class PrescriptionLine:
    def __init__(self, medicine_code: str, quantity: int) -> None:
        if not isinstance(medicine_code, str) or not medicine_code.strip():
            raise PharmacyError(
                f"Invalid medicine code on line: {medicine_code!r}. "
                "Must be a non-empty string."
            )
        if (
            isinstance(quantity, bool)
            or not isinstance(quantity, int)
            or quantity <= 0
        ):
            raise InvalidQuantityError(quantity, "prescription line quantity")

        self._medicine_code = medicine_code.strip()
        self._quantity = quantity

    @property
    def medicine_code(self) -> str:
        return self._medicine_code

    @property
    def quantity(self) -> int:
        return self._quantity

    def __repr__(self) -> str:
        return (
            f"PrescriptionLine(medicine_code={self._medicine_code!r}, "
            f"quantity={self._quantity})"
        )

    def __str__(self) -> str:
        return f"{self._medicine_code} x {self._quantity}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PrescriptionLine):
            return NotImplemented
        return (
            self._medicine_code == other._medicine_code
            and self._quantity == other._quantity
        )

    def __hash__(self) -> int:
        return hash(("PrescriptionLine", self._medicine_code, self._quantity))


class Prescription:
    def __init__(
        self,
        patient_id: str,
        branch: Branch,
        prescriber_code: str | None = None,
        lines: list[PrescriptionLine] | None = None,
        id: int | None = None,
        status: str = PENDING,
    ) -> None:
        if not isinstance(patient_id, str) or not patient_id.strip():
            raise PharmacyError(
                f"Invalid patient id: {patient_id!r}. "
                "Patient id must be a non-empty string."
            )

        if not isinstance(branch, Branch):
            raise PharmacyError(
                f"Invalid branch: {branch!r}. Must be a Branch instance."
            )

        if prescriber_code is not None:
            if not isinstance(prescriber_code, str):
                raise PharmacyError(
                    f"Invalid prescriber code: {prescriber_code!r}. "
                    "Must be a string or None."
                )
            prescriber_code = prescriber_code.strip() or None

        if status not in _VALID_STATUSES:
            raise PharmacyError(
                f"Invalid status: {status!r}. "
                f"Must be one of {sorted(_VALID_STATUSES)}."
            )

        if id is not None and (
            isinstance(id, bool) or not isinstance(id, int) or id < 0
        ):
            raise PharmacyError(
                f"Invalid prescription id: {id!r}. "
                "Must be a whole number of 0 or more, or None."
            )

        self._patient_id = patient_id.strip()
        self._branch = branch
        self._prescriber_code = prescriber_code
        self._id = id
        self._status = status
        self._lines: list[PrescriptionLine] = []

        if lines:
            for line in lines:
                if not isinstance(line, PrescriptionLine):
                    raise PharmacyError(
                        f"Invalid prescription line: {line!r}. "
                        "Must be a PrescriptionLine instance."
                    )
                self._lines.append(line)

    @property
    def id(self) -> int | None:
        return self._id

    @property
    def patient_id(self) -> str:
        return self._patient_id

    @property
    def branch(self) -> Branch:
        return self._branch

    @property
    def prescriber_code(self) -> str | None:
        return self._prescriber_code

    @property
    def status(self) -> str:
        return self._status

    @property
    def lines(self) -> tuple[PrescriptionLine, ...]:
        return tuple(self._lines)

    def add_line(self, medicine_code: str, quantity: int) -> PrescriptionLine:
        line = PrescriptionLine(medicine_code, quantity)
        self._lines.append(line)
        return line

    def has_lines(self) -> bool:
        return len(self._lines) > 0

    def validate(self) -> None:
        if not self._lines:
            raise EmptyPrescriptionError()

    def mark_dispensed(self) -> None:
        if self._status == DISPENSED:
            raise AlreadyDispensedError(self._id)
        if self._status == CANCELLED:
            raise CancelledPrescriptionError(self._id, action="dispense")
        self.validate()
        self._status = DISPENSED

    def cancel(self) -> None:
        if self._status == DISPENSED:
            raise AlreadyDispensedError(self._id)
        if self._status == CANCELLED:
            raise CancelledPrescriptionError(self._id, action="cancel")
        self._status = CANCELLED

    def __repr__(self) -> str:
        return (
            f"Prescription(id={self._id!r}, "
            f"patient_id={self._patient_id!r}, "
            f"branch={self._branch.name!r}, "
            f"prescriber_code={self._prescriber_code!r}, "
            f"status={self._status!r}, lines={self._lines!r})"
        )

    def __str__(self) -> str:
        ident = self._id if self._id is not None else "(unsaved)"
        return (
            f"Rx {ident} for {self._patient_id} "
            f"[{self._status}] {len(self._lines)} line(s)"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Prescription):
            return NotImplemented
        if self._id is not None and other._id is not None:
            return self._id == other._id
        return self is other

    def __hash__(self) -> int:
        if self._id is not None:
            return hash(("Prescription", self._id))
        return id(self)