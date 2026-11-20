"""Role E: repository tests using an in-memory database, plus one reconnect test on a file."""
import os
import sqlite3
import tempfile
import unittest

from pharmacy.data.repository import Repository
from pharmacy.domain import (
    ControlledMedicine, DuplicateMedicineError, InsufficientStockError,
    OrdinaryMedicine, make_medicine,
)
from tests.fixtures import MAIN, SATELLITE, make_repo


class MedicineStorageTests(unittest.TestCase):
    def setUp(self):
        self.repo = make_repo()
        self.addCleanup(self.repo.conn.close)

    def test_duplicate_code_raises_domain_error(self):
        with self.assertRaises(DuplicateMedicineError):
            self.repo.add_medicine(make_medicine("MED-A", "Again", 100, 1, False))

    def test_loaded_medicine_has_right_subclass(self):
        self.assertIsInstance(self.repo.get_medicine("MED-A"), OrdinaryMedicine)
        self.assertIsInstance(self.repo.get_medicine("CTL-A"), ControlledMedicine)

    def test_unknown_medicine_returns_none(self):
        self.assertIsNone(self.repo.get_medicine("NOPE"))

    def test_list_medicines(self):
        self.assertEqual([m.code for m in self.repo.list_medicines()], ["CTL-A", "MED-A", "MED-B"])


class ConstraintTests(unittest.TestCase):
    """The database is the second layer of defence: bad rows are refused even if Python is bypassed."""

    def setUp(self):
        self.repo = make_repo()
        self.addCleanup(self.repo.conn.close)

    def test_price_must_be_positive(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.repo.conn.execute(
                "INSERT INTO medicines VALUES ('X1','x',0,1,0)")

    def test_reorder_level_cannot_be_negative(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.repo.conn.execute(
                "INSERT INTO medicines VALUES ('X2','x',10,-1,0)")

    def test_negative_stock_refused(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.repo.conn.execute(
                "UPDATE stock SET quantity = -1 WHERE branch_id = 1 AND medicine_code = 'MED-A'")

    def test_status_must_be_one_of_three(self):
        self.repo.conn.execute("INSERT INTO prescriptions (patient_id, branch_id, status) VALUES ('PT-1',1,'pending')")
        with self.assertRaises(sqlite3.IntegrityError):
            self.repo.conn.execute("UPDATE prescriptions SET status='lost' WHERE id=1")

    def test_line_quantity_must_be_positive(self):
        self.repo.conn.execute("INSERT INTO prescriptions (patient_id, branch_id) VALUES ('PT-1',1)")
        with self.assertRaises(sqlite3.IntegrityError):
            self.repo.conn.execute(
                "INSERT INTO prescription_lines (prescription_id, medicine_code, quantity) VALUES (1,'MED-A',0)")

    def test_foreign_key_on_stock(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.repo.conn.execute("INSERT INTO stock VALUES (99,'MED-A',5)")

    def test_unlisted_prescriber_code_can_be_stored(self):
        # prescriber_code has no foreign key, so rejection happens at dispense time
        self.repo.conn.execute(
            "INSERT INTO prescriptions (patient_id, branch_id, prescriber_code) VALUES ('PT-1',1,'PRB-999')")


class StockTests(unittest.TestCase):
    def setUp(self):
        self.repo = make_repo()
        self.addCleanup(self.repo.conn.close)

    def test_add_stock_creates_and_increases(self):
        self.repo.add_stock(SATELLITE, "MED-B", 7)
        self.assertEqual(self.repo.get_stock(SATELLITE, "MED-B"), 7)
        self.repo.add_stock(SATELLITE, "MED-B", 3)
        self.assertEqual(self.repo.get_stock(SATELLITE, "MED-B"), 10)

    def test_get_stock_missing_row_is_zero(self):
        self.assertEqual(self.repo.get_stock(SATELLITE, "CTL-A"), 0)

    def test_reduce_stock(self):
        self.repo.reduce_stock(MAIN, "MED-B", 2)
        self.assertEqual(self.repo.get_stock(MAIN, "MED-B"), 10)

    def test_reduce_stock_oversell_raises_and_changes_nothing(self):
        with self.assertRaises(InsufficientStockError) as ctx:
            self.repo.reduce_stock(MAIN, "MED-B", 50)
        self.assertEqual((ctx.exception.requested, ctx.exception.available), (50, 12))
        self.assertEqual(self.repo.get_stock(MAIN, "MED-B"), 12)

    def test_low_stock_uses_less_than_or_equal(self):
        self.repo.reduce_stock(MAIN, "MED-B", 7)      # 12 -> 5, reorder level 5
        rows = self.repo.list_low_stock()
        self.assertEqual([(r["branch_id"], r["medicine_code"]) for r in rows], [(MAIN, "MED-B")])

    def test_low_stock_branch_filter(self):
        self.repo.reduce_stock(SATELLITE, "MED-A", 5)  # 10 -> 5 = reorder level
        self.repo.reduce_stock(MAIN, "MED-B", 7)
        self.assertEqual(len(self.repo.list_low_stock()), 2)
        self.assertEqual(len(self.repo.list_low_stock(SATELLITE)), 1)


class TransactionTests(unittest.TestCase):
    def setUp(self):
        self.repo = make_repo()
        self.addCleanup(self.repo.conn.close)

    def test_commit_on_success(self):
        with self.repo.transaction():
            self.repo.add_stock(MAIN, "MED-B", 8)
        self.assertEqual(self.repo.get_stock(MAIN, "MED-B"), 20)

    def test_rollback_on_exception(self):
        with self.assertRaises(RuntimeError):
            with self.repo.transaction():
                self.repo.add_stock(MAIN, "MED-B", 8)
                raise RuntimeError("boom")
        self.assertEqual(self.repo.get_stock(MAIN, "MED-B"), 12)

    def test_methods_do_not_commit_by_themselves(self):
        self.repo.conn.execute("BEGIN")
        self.repo.add_stock(MAIN, "MED-B", 8)
        self.repo.conn.execute("ROLLBACK")
        self.assertEqual(self.repo.get_stock(MAIN, "MED-B"), 12)

    def test_prescription_header_and_lines_saved_together(self):
        with self.repo.transaction():
            rid = self.repo.create_prescription("PT-1", MAIN, "PRB-001", [("MED-A", 1), ("MED-B", 2)])
        rx = self.repo.get_prescription(rid)
        self.assertEqual([(l.medicine_code, l.quantity) for l in rx.lines], [("MED-A", 1), ("MED-B", 2)])
        self.assertEqual(rx.status, "pending")

    def test_failed_prescription_leaves_no_header(self):
        with self.assertRaises(sqlite3.IntegrityError):
            with self.repo.transaction():
                self.repo.create_prescription("PT-1", MAIN, "PRB-001", [("MED-A", 1), ("NO-SUCH", 2)])
        self.assertEqual(self.repo.conn.execute("SELECT COUNT(*) FROM prescriptions").fetchone()[0], 0)
        self.assertEqual(self.repo.conn.execute("SELECT COUNT(*) FROM prescription_lines").fetchone()[0], 0)


class PersistenceTests(unittest.TestCase):
    def test_data_survives_reconnect(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "test.db")
            repo = make_repo(path)
            with repo.transaction():
                repo.create_prescription("PT-1", MAIN, "PRB-001", [("MED-A", 3)])
            repo.conn.close()

            reopened = Repository(path)
            self.assertEqual(reopened.get_stock(MAIN, "MED-A"), 100)
            self.assertIsNotNone(reopened.get_medicine("CTL-A"))
            self.assertEqual(len(reopened.list_pending_prescriptions()), 1)
            reopened.conn.close()

    def test_seed_loads_once(self):
        repo = Repository(":memory:")
        repo.load_seed()
        repo.load_seed()  # second call must not duplicate or crash
        self.assertEqual(len(repo.list_medicines()), 8)
        self.assertEqual(len(repo.list_branches()), 2)
        self.assertTrue(repo.list_low_stock())  # seed promises at least one low-stock row
        self.assertEqual(repo.list_prescriber_codes(), ["PRB-001", "PRB-002", "PRB-003"])


if __name__ == "__main__":
    unittest.main()
