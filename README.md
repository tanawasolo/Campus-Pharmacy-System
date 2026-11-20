# Campus Pharmacy System

A multi branch campus pharmacy system for registering medicines, receiving stock, writing prescriptions and dispensing them safely. Built for CSC2105 with Python OOP, SQLite and tkinter.

**Key idea:** a prescription is dispensed in full or not at all. If any line fails (not enough stock or a controlled medicine from an unlisted prescriber) nothing is changed.

## Features

- Register ordinary and controlled medicines
- Receive stock per branch (Main Campus, Satellite Clinic)
- Create prescriptions with one or more lines
- Dispense or cancel pending prescriptions
- Low-stock report with an optional branch filter
- Data saved in SQLite, so it is still there after the app is closed

## Business rules

| Rule | Where it is enforced |
|---|---|
| Unit price must be greater than 0; reorder level 0 or more | Python (`Medicine`) and database `CHECK` |
| Stock and line quantities cannot be negative or zero where a positive number is required | Python and database `CHECK` |
| A prescription needs at least one line | Python (`Prescription.validate`) |
| Only a pending prescription can be dispensed or cancelled | Python (`Prescription`) |
| Controlled medicines need a prescriber on the allow-list (`PRB-001`, ...) | Service (`dispense`) |
| Dispensing is atomic: all lines succeed or everything is rolled back | Service transaction |

## Requirements

Python 3, standard library only (`sqlite3` and `tkinter` ship with Python). Nothing to `pip install`.

On some Linux systems tkinter is a separate package: `sudo apt install python3-tk`.
On Windows, use `py` in place of `python` if `python` is not recognised.

Run every command from the project root (the folder containing `pharmacy/` and `tests/`).

## Quick start

```
python -c "from pharmacy.data.repository import Repository; Repository('pharmacy.db').load_seed()"
python -m pharmacy.ui.app
```

The details of each step follow.

## How to create the database

```
python -c "from pharmacy.data.repository import Repository; Repository('pharmacy.db'); print('Database created: pharmacy.db')"
```

This runs `pharmacy/data/schema.sql` and creates the six tables (medicines, branches, stock, prescribers, prescriptions, prescription_lines). It is safe to run more than once.

To start again from nothing, delete `pharmacy.db` and repeat this step.

## How to load sample data

```
python -c "from pharmacy.data.repository import Repository; Repository('pharmacy.db').load_seed(); print('Sample data loaded')"
```

This runs `pharmacy/data/seed.sql`. All data is fictional:

- 2 branches: Main Campus, Satellite Clinic
- 8 medicines: 6 ordinary (`MED-001` to `MED-006`) and 2 controlled (`CTL-001`, `CTL-002`)
- 3 prescribers: `PRB-001`, `PRB-002`, `PRB-003`
- 3 pending prescriptions (`PT-0001` to `PT-0003`)
- Stock rows, some at or below their reorder level so the Low Stock screen is not empty

Loading twice does nothing the second time.

## How to run the app

```
python -m pharmacy.ui.app
```

The window has five tabs: **Register Medicine**, **Receive Stock**, **Create Prescription**, **Dispense** and **Low Stock**. Every error appears as a readable message box. Data is stored in `pharmacy.db`.

### Suggested demo walkthrough

1. Register Medicine: add a new medicine, then try a price of 0 to see the rejection.
2. Receive Stock: add stock of it to a branch.
3. Create Prescription: enter `PRB-001`, add two lines, save (Save stays disabled until a line exists).
4. Dispense: select `PT-0001` and dispense it (controlled medicine, listed prescriber).
5. Dispense: select `PT-0002` and dispense it. It is rejected because `PRB-999` is not on the allow-list, and nothing changes.
6. Low Stock: view the list, then filter by branch.
7. Close and reopen the app: everything is still there.

## How to run the tests

```
python -m unittest discover
```

Add `-v` to see every test name. The tests use an in-memory database, so they never touch `pharmacy.db`.

| File | What it proves |
|---|---|
| `tests/test_domain.py` | Validation, status rules, polymorphism, allow-list (no database) |
| `tests/test_repository.py` | Constraints, transactions, low stock, data surviving a reconnect |
| `tests/test_dispensing.py` | Every rejection case and the atomic rollback |
| `tests/fixtures.py` | The same fictional test data on every run |

## Project structure

```
pharmacy/
  domain/      Business rules: medicines, stock, prescriptions, exceptions (no database)
  data/        schema.sql, seed.sql, repository.py (all SQL lives here)
  services/    dispensing_service.py: workflows and atomic dispensing
  ui/          tkinter screens (no SQL, no business rules)
tests/         Unit and integration tests
docs/          contract.md, test_checklist.md, defect_log.md
```

Layers only depend downwards: `ui` calls `services`, `services` calls `data` and `domain`, and `domain` depends on nothing. The agreed names are in `docs/contract.md`.

## Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'pharmacy'` | You are not in the project root. `cd` into the folder that contains `pharmacy/`. |
| `No module named 'tkinter'` | Install it: `sudo apt install python3-tk` (Linux). On Windows or macOS, reinstall Python from python.org with tcl/tk selected. |
| `unable to open database file` | Run from a folder you can write to. |
| Sample data looks changed or wrong | Delete `pharmacy.db`, then redo the create and load steps. |
| A test fails | Note the error and add it to `docs/defect_log.md`. |

## Team

| Role | Owns |
|---|---|
| A | Domain model |
| B | SQLite schema and repository |
| C | Dispensing service and transactions |
| D | tkinter screens |
| E | Tests, test data, README, logs |