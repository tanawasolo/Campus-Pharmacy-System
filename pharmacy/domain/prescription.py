"""Role A: prescription, lines and status lifecycle."""
from pharmacy.domain.exceptions import (
    AlreadyDispensedError,
    CancelledPrescriptionError,
    EmptyPrescriptionError,
    InvalidQuantityError,
)

PENDING, DISPENSED, CANCELLED = "pending", "dispensed", "cancelled"


class PrescriptionLine:
    def __init__(self, medicine_code, quantity):
        # TODO: quantity must be an int > 0 (InvalidQuantityError)
        raise NotImplementedError


class Prescription:
    def __init__(self, patient_id, branch_id, prescriber_code, lines=None, status=PENDING, id=None):
        # TODO: store fields; status only changes through the methods below
        raise NotImplementedError

    def add_line(self, line):
        raise NotImplementedError  # TODO

    def mark_dispensed(self):
        """TODO: AlreadyDispensedError / CancelledPrescriptionError unless pending."""
        raise NotImplementedError

    def cancel(self):
        """TODO: allowed only when pending; otherwise raise the matching error."""
        raise NotImplementedError
