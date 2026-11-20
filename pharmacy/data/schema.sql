PRAGMA foreign_keys = ON;

-- SQLite dialect
CREATE TABLE IF NOT EXISTS medicines (
  code TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  unit_price REAL NOT NULL,
  reorder_level INTEGER NOT NULL,
  is_controlled INTEGER NOT NULL DEFAULT 0 CHECK (is_controlled IN (0, 1)),
  CONSTRAINT medicines_unit_price_positive CHECK (unit_price > 0),
  CONSTRAINT medicines_reorder_level_nonnegative CHECK (reorder_level >= 0)
);

CREATE TABLE IF NOT EXISTS branches (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS stock (
  branch_id INTEGER NOT NULL REFERENCES branches(id),
  medicine_code TEXT NOT NULL REFERENCES medicines(code),
  quantity INTEGER NOT NULL CHECK (quantity >= 0),
  PRIMARY KEY (branch_id, medicine_code)
);

CREATE TABLE IF NOT EXISTS prescribers (
  code TEXT PRIMARY KEY,
  name TEXT
);

-- prescriber_code is deliberately not a foreign key: an unlisted code must be
-- storable so it can be rejected at dispense time.
CREATE TABLE IF NOT EXISTS prescriptions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  patient_id TEXT NOT NULL,
  branch_id INTEGER NOT NULL REFERENCES branches(id),
  prescriber_code TEXT,
  status TEXT NOT NULL DEFAULT 'pending'
    CHECK (status = 'pending' OR status = 'dispensed' OR status = 'cancelled')
);

CREATE TABLE IF NOT EXISTS prescription_lines (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  prescription_id INTEGER NOT NULL REFERENCES prescriptions(id),
  medicine_code TEXT NOT NULL REFERENCES medicines(code),
  quantity INTEGER NOT NULL CHECK (quantity > 0)
);
