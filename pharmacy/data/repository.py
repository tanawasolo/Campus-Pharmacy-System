"""Role B: all SQLite access. No other module may contain SQL.

Rules from docs/contract.md:
- connect with isolation_level=None and PRAGMA foreign_keys = ON
- methods NEVER commit; only transaction() commits or rolls back
"""
import sqlite3
from contextlib import contextmanager
from pathlib import Path

from pharmacy.domain.branch import Branch
from pharmacy.domain.exceptions import DuplicateMedicineError, InsufficientStockError
from pharmacy.domain.medicine import make_medicine

DATA_DIR = Path(__file__).parent
SCHEMA_PATH = DATA_DIR / "schema.sql"
SEED_PATH = DATA_DIR / "seed.sql"


class Repository:
    def __init__(self, db_path="pharmacy.db"):
        self.db_path = str(db_path)
        self.conn = sqlite3.connect(self.db_path, isolation_level=None)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.init_db()

    def init_db(self):
        """Run schema.sql (CREATE TABLE IF NOT EXISTS)."""
        schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
        self.conn.executescript(schema_sql)

    def load_seed(self):
        """Run seed.sql once on an empty database."""
        cur = self.conn.execute("SELECT COUNT(*) AS n FROM medicines")
        row = cur.fetchone()
        if row and row["n"] > 0:
            return
        seed_sql = SEED_PATH.read_text(encoding="utf-8")
        self.conn.executescript(seed_sql)

    @contextmanager
    def transaction(self):
        """BEGIN; yield; COMMIT on success, ROLLBACK and re-raise on error."""
        self.conn.execute("BEGIN")
        try:
            yield
        except Exception:
            self.conn.execute("ROLLBACK")
            raise
        else:
            self.conn.execute("COMMIT")

    # --- medicines ---
    def add_medicine(self, med):
        try:
            self.conn.execute(
                """
                INSERT INTO medicines (code, name, unit_price, reorder_level, is_controlled)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    med.code,
                    med.name,
                    med.unit_price,
                    med.reorder_level,
                    1 if getattr(med, "is_controlled", False) else 0,
                ),
            )
        except sqlite3.IntegrityError as exc:
            msg = str(exc).lower()
            if "unique" in msg and "medicines.code" in msg or "primary key" in msg:
                raise DuplicateMedicineError(med.code) from exc
            raise

    def get_medicine(self, code):
        row = self.conn.execute(
            "SELECT code, name, unit_price, reorder_level, is_controlled FROM medicines WHERE code = ?",
            (code,),
        ).fetchone()
        if row is None:
            return None
        return make_medicine(
            row["code"],
            row["name"],
            row["unit_price"],
            row["reorder_level"],
            bool(row["is_controlled"]),
        )

    def list_medicines(self):
        rows = self.conn.execute(
            "SELECT code, name, unit_price, reorder_level, is_controlled FROM medicines ORDER BY code"
        ).fetchall()
        return [
            make_medicine(
                r["code"], r["name"], r["unit_price"], r["reorder_level"], bool(r["is_controlled"])
            )
            for r in rows
        ]

    # --- branches ---
    def add_branch(self, name):
        cur = self.conn.execute("INSERT INTO branches (name) VALUES (?)", (name,))
        return cur.lastrowid

    def list_branches(self):
        rows = self.conn.execute("SELECT id, name FROM branches ORDER BY id").fetchall()
        return [Branch(r["name"], id=r["id"]) for r in rows]

    # --- stock ---
    def add_stock(self, branch_id, code, qty):
        cur = self.conn.execute(
            "SELECT quantity FROM stock WHERE branch_id = ? AND medicine_code = ?",
            (branch_id, code),
        ).fetchone()
        if cur is None:
            self.conn.execute(
                "INSERT INTO stock (branch_id, medicine_code, quantity) VALUES (?, ?, ?)",
                (branch_id, code, qty),
            )
        else:
            new_qty = cur["quantity"] + qty
            self.conn.execute(
                "UPDATE stock SET quantity = ? WHERE branch_id = ? AND medicine_code = ?",
                (new_qty, branch_id, code),
            )

    def reduce_stock(self, branch_id, code, qty):
        row = self.conn.execute(
            "SELECT quantity FROM stock WHERE branch_id = ? AND medicine_code = ?",
            (branch_id, code),
        ).fetchone()
        available = row["quantity"] if row else 0
        if qty > available:
            raise InsufficientStockError(qty, available, medicine_code=code)
        new_qty = available - qty
        self.conn.execute(
            "UPDATE stock SET quantity = ? WHERE branch_id = ? AND medicine_code = ?",
            (new_qty, branch_id, code),
        )

    def get_stock(self, branch_id, code):
        row = self.conn.execute(
            "SELECT quantity FROM stock WHERE branch_id = ? AND medicine_code = ?",
            (branch_id, code),
        ).fetchone()
        if row is None:
            return 0
        return row["quantity"]

    # --- prescriptions ---
    def _extract_line(self, line):
        if isinstance(line, tuple) and len(line) == 2:
            return line[0], line[1]
        if isinstance(line, dict):
            code = line.get("medicine_code", line.get("code"))
            qty = line.get("quantity", line.get("qty"))
            return code, qty
        code = getattr(line, "medicine_code", None)
        qty = getattr(line, "quantity", None)
        return code, qty

    def create_prescription(self, patient_id, branch_id, prescriber_code, lines):
        lines_list = list(lines)
        cur = self.conn.execute(
            """
            INSERT INTO prescriptions (patient_id, branch_id, prescriber_code, status)
            VALUES (?, ?, ?, 'pending')
            """,
            (patient_id, branch_id, prescriber_code),
        )
        prescription_id = cur.lastrowid
        for line in lines_list:
            med_code, qty = self._extract_line(line)
            self.conn.execute(
                """
                INSERT INTO prescription_lines (prescription_id, medicine_code, quantity)
                VALUES (?, ?, ?)
                """,
                (prescription_id, med_code, qty),
            )
        return prescription_id

    def _build_prescription(self, row):
        line_rows = self.conn.execute(
            "SELECT medicine_code, quantity FROM prescription_lines WHERE prescription_id = ? ORDER BY id",
            (row["id"],),
        ).fetchall()
        lines_data = [(r["medicine_code"], r["quantity"]) for r in line_rows]
        try:
            from pharmacy.domain.prescription import Prescription, PrescriptionLine

            p = Prescription(
                row["patient_id"],
                row["branch_id"],
                row["prescriber_code"],
                lines=None,
                status=row["status"],
                id=row["id"],
            )
            # try to populate lines if constructor doesn't
            existing = getattr(p, "lines", None)
            if existing is None or len(existing) == 0:
                for code, qty in lines_data:
                    try:
                        p.add_line(PrescriptionLine(code, qty))
                    except Exception:
                        pass
            return p
        except Exception:
            # Fallback simple object if domain Prescription not ready
            class _PrescriptionView:
                pass

            p = _PrescriptionView()
            p.id = row["id"]
            p.patient_id = row["patient_id"]
            p.branch_id = row["branch_id"]
            p.prescriber_code = row["prescriber_code"]
            p.status = row["status"]
            p.lines = [{"medicine_code": c, "quantity": q} for c, q in lines_data]
            return p

    def get_prescription(self, id):
        row = self.conn.execute(
            "SELECT id, patient_id, branch_id, prescriber_code, status FROM prescriptions WHERE id = ?",
            (id,),
        ).fetchone()
        if row is None:
            return None
        return self._build_prescription(row)

    def list_pending_prescriptions(self):
        rows = self.conn.execute(
            "SELECT id, patient_id, branch_id, prescriber_code, status FROM prescriptions WHERE status = 'pending' ORDER BY id"
        ).fetchall()
        return [self._build_prescription(r) for r in rows]

    def set_status(self, id, status):
        self.conn.execute("UPDATE prescriptions SET status = ? WHERE id = ?", (status, id))

    # --- queries ---
    def list_low_stock(self, branch_id=None):
        base = """
            SELECT s.branch_id, b.name AS branch_name, s.medicine_code, m.name AS medicine_name,
                   s.quantity, m.reorder_level
            FROM stock s
            JOIN medicines m ON m.code = s.medicine_code
            JOIN branches b ON b.id = s.branch_id
            WHERE s.quantity <= m.reorder_level
        """
        params = []
        if branch_id is not None:
            base += " AND s.branch_id = ?"
            params.append(branch_id)
        base += " ORDER BY b.id, s.medicine_code"
        rows = self.conn.execute(base, params).fetchall()
        return [dict(r) for r in rows]

    def list_prescriber_codes(self):
        rows = self.conn.execute("SELECT code FROM prescribers ORDER BY code").fetchall()
        return [r["code"] for r in rows]
