"""Role E: the most important tests. Every rejection case and the atomic rollback."""
import unittest

from pharmacy.domain import (
    AlreadyDispensedError, Branch, CancelledPrescriptionError, EmptyPrescriptionError,
    InsufficientStockError, InvalidQuantityError, Prescription, UnauthorisedPrescriberError,
    make_medicine, DISPENSED, CANCELLED, PENDING, DuplicateMedicineError,
)
from tests.fixtures import ALLOWED, MAIN, UNLISTED, make_service, new_prescription, snapshot


class DispenseTests(unittest.TestCase):
    def setUp(self):
        self.service, self.repo = make_service()
        self.addCleanup(self.repo.conn.close)

    def status(self, rid):
        return self.repo.get_prescription(rid).status

    # --- success ---
    def test_successful_dispense_reduces_every_line_and_sets_status(self):
        rid = new_prescription(self.service, [("MED-A", 10), ("MED-B", 2)])
        self.service.dispense(rid)
        self.assertEqual(self.repo.get_stock(MAIN, "MED-A"), 90)
        self.assertEqual(self.repo.get_stock(MAIN, "MED-B"), 10)
        self.assertEqual(self.status(rid), DISPENSED)

    def test_controlled_medicine_with_listed_prescriber(self):
        rid = new_prescription(self.service, [("CTL-A", 2)], prescriber=ALLOWED)
        self.service.dispense(rid)
        self.assertEqual(self.repo.get_stock(MAIN, "CTL-A"), 18)
        self.assertEqual(self.status(rid), DISPENSED)

    def test_ordinary_medicine_needs_no_prescriber(self):
        rid = new_prescription(self.service, [("MED-A", 1)], prescriber=None)
        self.service.dispense(rid)
        self.assertEqual(self.status(rid), DISPENSED)

    # --- rejections ---
    def test_oversell_rejected(self):
        rid = new_prescription(self.service, [("MED-B", 50)])
        before = snapshot(self.repo)
        with self.assertRaises(InsufficientStockError) as ctx:
            self.service.dispense(rid)
        self.assertEqual((ctx.exception.requested, ctx.exception.available), (50, 12))
        self.assertEqual(snapshot(self.repo), before)

    def test_controlled_with_unlisted_prescriber_rejected(self):
        rid = new_prescription(self.service, [("CTL-A", 1)], prescriber=UNLISTED)
        before = snapshot(self.repo)
        with self.assertRaises(UnauthorisedPrescriberError):
            self.service.dispense(rid)
        self.assertEqual(snapshot(self.repo), before)
        self.assertEqual(self.status(rid), PENDING)

    def test_controlled_with_no_prescriber_rejected(self):
        rid = new_prescription(self.service, [("CTL-A", 1)], prescriber=None)
        with self.assertRaises(UnauthorisedPrescriberError):
            self.service.dispense(rid)

    def test_re_dispense_rejected(self):
        rid = new_prescription(self.service, [("MED-A", 1)])
        self.service.dispense(rid)
        with self.assertRaises(AlreadyDispensedError):
            self.service.dispense(rid)
        self.assertEqual(self.repo.get_stock(MAIN, "MED-A"), 99)  # not reduced twice

    def test_dispense_cancelled_rejected(self):
        rid = new_prescription(self.service, [("MED-A", 1)])
        self.service.cancel(rid)
        with self.assertRaises(CancelledPrescriptionError):
            self.service.dispense(rid)
        self.assertEqual(self.repo.get_stock(MAIN, "MED-A"), 100)

    def test_cancel_dispensed_rejected(self):
        rid = new_prescription(self.service, [("MED-A", 1)])
        self.service.dispense(rid)
        with self.assertRaises(AlreadyDispensedError):
            self.service.cancel(rid)
        self.assertEqual(self.status(rid), DISPENSED)

    def test_cancel_twice_rejected(self):
        rid = new_prescription(self.service, [("MED-A", 1)])
        self.service.cancel(rid)
        with self.assertRaises(CancelledPrescriptionError):
            self.service.cancel(rid)

    def test_cancel_pending_works(self):
        rid = new_prescription(self.service, [("MED-A", 1)])
        self.service.cancel(rid)
        self.assertEqual(self.status(rid), CANCELLED)

    def test_empty_prescription_rejected(self):
        rx = Prescription("PT-1", Branch("Main Campus", id=MAIN), ALLOWED)
        with self.assertRaises(EmptyPrescriptionError):
            self.service.create_prescription(rx)
        self.assertEqual(len(self.repo.list_pending_prescriptions()), 0)

    # --- atomicity ---
    def test_rollback_leaves_stock_untouched_when_line_2_oversells(self):
        rid = new_prescription(self.service, [("MED-A", 10), ("MED-B", 50)])
        before = snapshot(self.repo)
        with self.assertRaises(InsufficientStockError):
            self.service.dispense(rid)
        self.assertEqual(snapshot(self.repo), before)          # line 1 NOT kept
        self.assertEqual(self.repo.get_stock(MAIN, "MED-A"), 100)
        self.assertEqual(self.status(rid), PENDING)

    def test_rollback_when_controlled_line_is_second_and_prescriber_unlisted(self):
        rid = new_prescription(self.service, [("MED-A", 10), ("CTL-A", 1)], prescriber=UNLISTED)
        before = snapshot(self.repo)
        with self.assertRaises(UnauthorisedPrescriberError):
            self.service.dispense(rid)
        self.assertEqual(snapshot(self.repo), before)

    def test_failed_dispense_can_be_retried_after_restocking(self):
        rid = new_prescription(self.service, [("MED-B", 20)])
        with self.assertRaises(InsufficientStockError):
            self.service.dispense(rid)
        self.service.receive_stock(MAIN, "MED-B", 10)
        self.service.dispense(rid)
        self.assertEqual(self.repo.get_stock(MAIN, "MED-B"), 2)


class OtherServiceTests(unittest.TestCase):
    def setUp(self):
        self.service, self.repo = make_service()
        self.addCleanup(self.repo.conn.close)

    def test_register_medicine(self):
        self.service.register_medicine(make_medicine("MED-Z", "Fictional Z", 100, 1, False))
        self.assertIsNotNone(self.repo.get_medicine("MED-Z"))

    def test_register_duplicate_medicine_rejected(self):
        with self.assertRaises(DuplicateMedicineError):
            self.service.register_medicine(make_medicine("MED-A", "Dup", 100, 1, False))

    def test_receive_stock(self):
        self.service.receive_stock(MAIN, "MED-B", 8)
        self.assertEqual(self.repo.get_stock(MAIN, "MED-B"), 20)

    def test_receive_stock_rejects_zero_negative_and_non_integer(self):
        for bad in (0, -4, 2.5, "3"):
            with self.subTest(qty=bad), self.assertRaises(InvalidQuantityError):
                self.service.receive_stock(MAIN, "MED-B", bad)
        self.assertEqual(self.repo.get_stock(MAIN, "MED-B"), 12)

    def test_low_stock(self):
        self.repo.reduce_stock(MAIN, "MED-B", 8)  # 12 -> 4 (reorder level 5)
        self.assertEqual([r["medicine_code"] for r in self.service.low_stock()], ["MED-B"])


if __name__ == "__main__":
    unittest.main()
