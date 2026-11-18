"""Role E: smoke test. Replace with real tests as each layer lands."""
import sqlite3
import unittest
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "pharmacy" / "data"


class SchemaSmokeTest(unittest.TestCase):
    def test_schema_and_seed_load(self):
        conn = sqlite3.connect(":memory:")
        conn.executescript((DATA / "schema.sql").read_text())
        conn.executescript((DATA / "seed.sql").read_text())
        count = conn.execute("SELECT COUNT(*) FROM medicines").fetchone()[0]
        self.assertEqual(count, 8)

    def test_modules_import(self):
        import pharmacy.domain.exceptions  # noqa: F401
        import pharmacy.domain.medicine  # noqa: F401
        import pharmacy.services.dispensing_service  # noqa: F401


if __name__ == "__main__":
    unittest.main()
