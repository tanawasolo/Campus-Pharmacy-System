"""Role B: all SQLite access. No other module may contain SQL.

Rules from docs/contract.md:
- connect with isolation_level=None and PRAGMA foreign_keys = ON
- methods NEVER commit; only transaction() commits or rolls back
"""
import sqlite3
from contextlib import contextmanager
from pathlib import Path

DATA_DIR = Path(__file__).parent
SCHEMA_PATH = DATA_DIR / "schema.sql"
SEED_PATH = DATA_DIR / "seed.sql"


class Repository:
    def __init__(self, db_path="pharmacy.db"):
        # TODO: connect, enable foreign keys, call init_db()
        raise NotImplementedError

    def init_db(self):
        """TODO: run schema.sql (CREATE TABLE IF NOT EXISTS)."""
        raise NotImplementedError

    def load_seed(self):
        """TODO: run seed.sql once on an empty database."""
        raise NotImplementedError

    @contextmanager
    def transaction(self):
        """TODO: BEGIN; yield; COMMIT on success, ROLLBACK and re-raise on error."""
        raise NotImplementedError
        yield  # pragma: no cover

    # TODO each of these, per docs/contract.md:
    # add_medicine, get_medicine (factory: Controlled vs Ordinary), list_medicines,
    # add_branch, list_branches, add_stock, reduce_stock, get_stock,
    # create_prescription, get_prescription, list_pending_prescriptions,
    # set_status, list_low_stock, list_prescriber_codes
