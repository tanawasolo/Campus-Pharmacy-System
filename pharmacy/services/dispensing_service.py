"""Role C: business workflows and atomic dispensing."""


from pharmacy.exceptions import (
    PharmacyError,
    EmptyPrescriptionError,
    InsufficientStockError,
    PrescriberNotAllowedError,
    PrescriptionStateError,
)
from pharmacy.domain.medicine import ControlledMedicine


class DispensingService:
    def __init__(self, repo):
        self.repo = repo    
        
    def register_medicine(self, medicine):
        """Validation already happens in the Medicine constructor (Role A)."""
        self.repo.add_medicine(medicine)
        return medicine

    def receive_stock(self, branch_id, medicine_id, quantity):
        """Add stock for a medicine at a branch."""
        if quantity <= 0:
            raise PharmacyError("Quantity received must be greater than 0.")
        self.repo.get_medicine(medicine_id)  # raises if it does not exist
        with self.repo.transaction():
            self.repo.add_stock(branch_id, medicine_id, quantity)

    def low_stock(self, branch_id=None):
        """Items at or below their reorder level, optionally for one branch."""
        items = self.repo.list_low_stock()
        if branch_id is not None:
            items = [i for i in items if i.branch_id == branch_id]
        return items
    def create_prescription(self, prescription):
        """Save a new pending prescription. At least one line is required."""
        if not prescription.lines:
            raise EmptyPrescriptionError(
                "A prescription must have at least one line."
            )
        with self.repo.transaction():
            self.repo.create_prescription(prescription)
        return prescription

    def list_pending(self):
        return self.repo.list_pending_prescriptions()

    def dispense(self, prescription_id):
        """Dispense a pending prescription, all lines or nothing."""
        with self.repo.transaction():
            # 1. load
            prescription = self.repo.get_prescription(prescription_id)

            # 2. status check
            if prescription.status == "dispensed":
                raise PrescriptionStateError(
                    "This prescription has already been dispensed."
                )
            if prescription.status == "cancelled":
                raise PrescriptionStateError(
                    "This prescription has been cancelled."
                )

            # 3. controlled-medicine check (allow-list)
            allowed = set(self.repo.list_prescriber_codes())
            for line in prescription.lines:
                medicine = self.repo.get_medicine(line.medicine_id)
                if isinstance(medicine, ControlledMedicine):
                    if prescription.prescriber_code not in allowed:
                        raise PrescriberNotAllowedError(
                            f"Prescriber '{prescription.prescriber_code}' is "
                            f"not allowed to prescribe {medicine.name}."
                        )

                # 4. reduce stock for every line
            for line in prescription.lines:
                available = self.repo.get_stock(
                    prescription.branch_id, line.medicine_id
                )
                if available < line.quantity:
                    raise InsufficientStockError(
                        f"Not enough stock for medicine {line.medicine_id}: "
                        f"need {line.quantity}, have {available}."
                    )
                self.repo.reduce_stock(
                    prescription.branch_id, line.medicine_id, line.quantity
                )

            # 5. mark dispensed
            self.repo.set_status(prescription_id, "dispensed")
    def cancel(self, prescription_id):
        """Cancel a prescription. Only pending ones can be cancelled."""
        with self.repo.transaction():
            prescription = self.repo.get_prescription(prescription_id)
            if prescription.status != "pending":
                raise PrescriptionStateError(
                    "Only pending prescriptions can be cancelled."
                )
            self.repo.set_status(prescription_id, "cancelled")