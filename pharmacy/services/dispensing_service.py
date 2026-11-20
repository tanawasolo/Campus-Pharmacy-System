"""DispensingService: the business workflows on top of the repository.

Every write runs inside repo.transaction(), because repository methods never
commit. dispense() checks the status, the prescriber allow-list for controlled
medicines and the stock for every line inside one transaction, so a prescription
is dispensed in full or not at all. Status rules come from Prescription
(mark_dispensed, cancel) and the allow-list rule from PrescriberRegistry.
"""

from __future__ import annotations

from pharmacy.domain import (
    CANCELLED,
    DISPENSED,
    InvalidQuantityError,
    PharmacyError,
    PrescriberRegistry,
    UnauthorisedPrescriberError,
)


class DispensingService:
    def __init__(self, repo) -> None:
        self.repo = repo

    def register_medicine(self, medicine):
        with self.repo.transaction():
            self.repo.add_medicine(medicine)
        return medicine

    def receive_stock(self, branch_id, medicine_code, quantity) -> None:
        if (
            isinstance(quantity, bool)
            or not isinstance(quantity, int)
            or quantity <= 0
        ):
            raise InvalidQuantityError(quantity, "stock receipt")
        self.repo.get_medicine(medicine_code)
        with self.repo.transaction():
            self.repo.add_stock(branch_id, medicine_code, quantity)

    def low_stock(self, branch_id=None):
        return self.repo.list_low_stock(branch_id)

    def create_prescription(self, prescription):
        prescription.validate()
        if prescription.branch.id is None:
            raise PharmacyError("The prescription's branch has not been saved.")
        with self.repo.transaction():
            return self.repo.create_prescription(
                prescription.patient_id,
                prescription.branch.id,
                prescription.prescriber_code,
                list(prescription.lines),
            )

    def list_pending(self):
        return self.repo.list_pending_prescriptions()

    def dispense(self, prescription_id) -> None:
        with self.repo.transaction():
            prescription = self.repo.get_prescription(prescription_id)
            prescription.mark_dispensed()

            registry = PrescriberRegistry(self.repo.list_prescriber_codes())
            for line in prescription.lines:
                medicine = self.repo.get_medicine(line.medicine_code)
                if (
                    medicine.requires_authorisation()
                    and not registry.is_allowed(prescription.prescriber_code)
                ):
                    raise UnauthorisedPrescriberError(
                        prescription.prescriber_code, medicine.code
                    )

            for line in prescription.lines:
                self.repo.reduce_stock(
                    prescription.branch.id, line.medicine_code, line.quantity
                )

            self.repo.set_status(prescription_id, DISPENSED)

    def cancel(self, prescription_id) -> None:
        with self.repo.transaction():
            prescription = self.repo.get_prescription(prescription_id)
            prescription.cancel()
            self.repo.set_status(prescription_id, CANCELLED)