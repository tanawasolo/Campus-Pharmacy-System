"""Role E: domain tests (no database)."""
import unittest

from pharmacy.domain import (
    AlreadyDispensedError, Branch, CancelledPrescriptionError, ControlledMedicine,
    EmptyPrescriptionError, InsufficientStockError, InvalidPriceError,
    InvalidQuantityError, InvalidReorderLevelError, Medicine, OrdinaryMedicine,
    PharmacyError, PrescriberRegistry, Prescription, PrescriptionLine, StockItem,
    make_medicine, PENDING, DISPENSED, CANCELLED,
)


class MedicineTests(unittest.TestCase):
    def test_abstract_base_cannot_be_created(self):
        with self.assertRaises(TypeError):
            Medicine("M", "x", 1, 1)

    def test_invalid_price_rejected_in_constructor(self):
        for bad in (0, -5, "abc", None, float("nan")):
            with self.subTest(price=bad), self.assertRaises(InvalidPriceError):
                OrdinaryMedicine("MED-1", "Test", bad, 5)

    def test_negative_reorder_level_rejected(self):
        with self.assertRaises(InvalidReorderLevelError):
            OrdinaryMedicine("MED-1", "Test", 100, -1)

    def test_setters_validate_after_construction(self):
        med = OrdinaryMedicine("MED-1", "Test", 100, 5)
        with self.assertRaises(InvalidPriceError):
            med.unit_price = -1
        with self.assertRaises(InvalidReorderLevelError):
            med.reorder_level = -3
        self.assertEqual(med.unit_price, 100)  # unchanged after the failed set

    def test_blank_code_and_name_rejected(self):
        with self.assertRaises(PharmacyError):
            OrdinaryMedicine("  ", "Test", 100, 5)
        with self.assertRaises(PharmacyError):
            OrdinaryMedicine("MED-1", "", 100, 5)

    def test_requires_authorisation_polymorphism(self):
        self.assertFalse(OrdinaryMedicine("M1", "a", 1, 0).requires_authorisation())
        self.assertTrue(ControlledMedicine("C1", "b", 1, 0).requires_authorisation())

    def test_category_and_str_overridden(self):
        o, c = OrdinaryMedicine("M1", "a", 1, 0), ControlledMedicine("C1", "b", 1, 0)
        self.assertEqual(o.category(), "Ordinary")
        self.assertEqual(c.category(), "Controlled")
        self.assertIn("Ordinary", str(o))
        self.assertIn("Controlled", str(c))

    def test_make_medicine_factory(self):
        self.assertIsInstance(make_medicine("M1", "a", 1, 0, False), OrdinaryMedicine)
        self.assertIsInstance(make_medicine("C1", "b", 1, 0, True), ControlledMedicine)
        self.assertTrue(make_medicine("C1", "b", 1, 0, True).is_controlled)


class StockItemTests(unittest.TestCase):
    def setUp(self):
        self.item = StockItem(Branch("Main", id=1), "MED-1", 10)

    def test_negative_starting_quantity_rejected(self):
        with self.assertRaises(InvalidQuantityError):
            StockItem(Branch("Main", id=1), "MED-1", -1)

    def test_add_and_remove(self):
        self.assertEqual(self.item.add(5), 15)
        self.assertEqual(self.item.remove(15), 0)

    def test_add_rejects_zero_and_negative(self):
        for bad in (0, -1):
            with self.subTest(n=bad), self.assertRaises(InvalidQuantityError):
                self.item.add(bad)

    def test_remove_more_than_available(self):
        with self.assertRaises(InsufficientStockError) as ctx:
            self.item.remove(11)
        self.assertEqual((ctx.exception.requested, ctx.exception.available), (11, 10))
        self.assertEqual(self.item.quantity, 10)

    def test_quantity_has_no_setter(self):
        with self.assertRaises(AttributeError):
            self.item.quantity = 99

    def test_is_low(self):
        self.assertTrue(self.item.is_low(10))
        self.assertFalse(self.item.is_low(9))


class PrescriptionTests(unittest.TestCase):
    def make(self, lines=True, status=PENDING):
        rx = Prescription("PT-1", Branch("Main", id=1), "PRB-001", id=1, status=status)
        if lines:
            rx.add_line("MED-1", 2)
        return rx

    def test_line_quantity_must_be_positive(self):
        for bad in (0, -1, 1.5, True):
            with self.subTest(q=bad), self.assertRaises(InvalidQuantityError):
                PrescriptionLine("MED-1", bad)

    def test_empty_prescription_fails_validate(self):
        with self.assertRaises(EmptyPrescriptionError):
            self.make(lines=False).validate()

    def test_blank_prescriber_stored_as_none(self):
        self.assertIsNone(Prescription("PT-1", Branch("M", id=1), "   ").prescriber_code)

    def test_pending_to_dispensed(self):
        rx = self.make()
        rx.mark_dispensed()
        self.assertEqual(rx.status, DISPENSED)

    def test_pending_to_cancelled(self):
        rx = self.make()
        rx.cancel()
        self.assertEqual(rx.status, CANCELLED)

    def test_cannot_dispense_twice(self):
        rx = self.make(status=DISPENSED)
        with self.assertRaises(AlreadyDispensedError):
            rx.mark_dispensed()

    def test_cannot_dispense_cancelled(self):
        with self.assertRaises(CancelledPrescriptionError):
            self.make(status=CANCELLED).mark_dispensed()

    def test_cannot_cancel_dispensed(self):
        with self.assertRaises(AlreadyDispensedError):
            self.make(status=DISPENSED).cancel()

    def test_cannot_cancel_twice(self):
        with self.assertRaises(CancelledPrescriptionError):
            self.make(status=CANCELLED).cancel()

    def test_status_has_no_setter(self):
        with self.assertRaises(AttributeError):
            self.make().status = DISPENSED

    def test_invalid_status_rejected(self):
        with self.assertRaises(PharmacyError):
            self.make(status="lost")


class PrescriberRegistryTests(unittest.TestCase):
    def setUp(self):
        self.reg = PrescriberRegistry({"PRB-001", "PRB-002"})

    def test_listed_code_allowed_ignoring_case_and_spaces(self):
        for ok in ("PRB-001", " prb-002 "):
            self.assertTrue(self.reg.is_allowed(ok))

    def test_unlisted_nonempty_string_not_allowed(self):
        self.assertFalse(self.reg.is_allowed("PRB-999"))

    def test_none_blank_and_non_strings_not_allowed(self):
        for bad in (None, "", "   ", 123):
            self.assertFalse(self.reg.is_allowed(bad))


if __name__ == "__main__":
    unittest.main()
