# Project contract

Everyone codes against these names. To change one: announce it in the group chat, then update this file in the same pull request.

## Exceptions (pharmacy/domain/exceptions.py)
All inherit PharmacyError. Each one builds its own message, so pass the values, not a sentence.

- InvalidPriceError(price)
- InvalidReorderLevelError(level)
- InvalidQuantityError(quantity, what="quantity", minimum=1)    use minimum=0 for stock quantities
- InsufficientStockError(requested, available, medicine_code=None)
- UnauthorisedPrescriberError(prescriber_code, medicine_code=None)
- AlreadyDispensedError(prescription_id)
- CancelledPrescriptionError(prescription_id, action="dispense")    use action="cancel" for a second cancel
- DuplicateMedicineError(code)
- EmptyPrescriptionError()    takes no arguments

## Repository (pharmacy/data/repository.py)
- add_medicine(med)
- get_medicine(code)
- list_medicines()
- add_branch(name)
- list_branches()
- add_stock(branch_id, code, qty)
- reduce_stock(branch_id, code, qty)    raises InsufficientStockError
- get_stock(branch_id, code)
- create_prescription(patient_id, branch_id, prescriber_code, lines) -> id
- get_prescription(id)
- list_pending_prescriptions()
- set_status(id, status)
- list_low_stock(branch_id=None)
- list_prescriber_codes()
- transaction()    context manager: BEGIN, then commit or rollback

Rule: repository methods never commit. Only transaction() commits or rolls back.
get_prescription(id) and list_pending_prescriptions() return Prescription objects with a Branch object and PrescriptionLine objects. Build the branch as Branch(name, id=row_id)
create_prescription(...) takes branch_id and plain lines for saving, and set_status(id, status) only stores the status. Status rules live in Prescription.mark_dispensed() and cancel(), so C calls those first, then set_status

## Service (pharmacy/services/dispensing_service.py)
register_medicine(...), receive_stock(...), create_prescription(...),
dispense(prescription_id), cancel(prescription_id), low_stock(...)

## Domain helpers (pharmacy/domain)
- make_medicine(code, name, unit_price, reorder_level, is_controlled) -> Medicine    in medicine.py. Builds the right subclass, use it in get_medicine
- medicine.is_controlled    in medicine.py. True or False, use it when saving the is_controlled column
- Branch(name, id=None)    in branch.py. id is None until the repository saves it. Build it as Branch(name, id=row_id)
- StockItem(branch, medicine_code, quantity=0)    in stock_item.py. branch is a Branch object, not an id. Read the id as item.branch.id. quantity is read-only, change it with add(n) and remove(n)
- PrescriptionLine(medicine_code, quantity)    in prescription.py. quantity above 0
- Prescription(patient_id, branch, prescriber_code=None, lines=None, id=None, status="pending")    in prescription.py. branch is a Branch object, not an id. Blank prescriber_code is stored as None
- rx.add_line(medicine_code, quantity)    adds one line
- rx.validate()    raises EmptyPrescriptionError with no lines. C calls it in create_prescription
- rx.mark_dispensed(), rx.cancel()    only way status changes. mark_dispensed also raises EmptyPrescriptionError
- PENDING, DISPENSED, CANCELLED    status constants in prescription.py. Use them, not raw strings
- PrescriberRegistry(allowed_codes=None)    in prescriber_registry.py. is_allowed(code) is True only for codes on the list, case and spaces ignored. None, blank and non-strings give False. Also add(code), remove(code), codes(). B loads prescribers into it, C calls is_allowed in dispense

## Decisions
1. The prescriber code is stored on the prescription.
2. Only pending prescriptions can be cancelled.
3. A prescription needs at least one line.
4. One actor (Pharmacy Staff), no login.
5. No transfers between branches.