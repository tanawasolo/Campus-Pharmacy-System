"""Role C: business workflows and atomic dispensing."""


class DispensingService:
    def __init__(self, repo, registry):
        self.repo = repo
        self.registry = registry

    def register_medicine(self, code, name, unit_price, reorder_level, is_controlled=False):
        raise NotImplementedError  # TODO

    def receive_stock(self, branch_id, medicine_code, quantity):
        raise NotImplementedError  # TODO

    def create_prescription(self, patient_id, branch_id, prescriber_code, lines):
        """TODO: EmptyPrescriptionError if no lines; header + lines in one transaction."""
        raise NotImplementedError

    def dispense(self, prescription_id):
        """TODO order: load, status checks, per-line allow-list check, reduce stock
        for every line, set status. All inside `with self.repo.transaction():`."""
        raise NotImplementedError

    def cancel(self, prescription_id):
        raise NotImplementedError  # TODO: pending only

    def low_stock(self, branch_id=None):
        raise NotImplementedError  # TODO
