"""Role E: reproducible test data. Fictional identifiers only.

Every call builds a fresh in-memory database with exactly the same rows, so
no test depends on another test or on seed.sql.

    branch 1  Main Campus        branch 2  Satellite Clinic
    MED-A  ordinary    price 500    reorder 5     stock: b1=100  b2=10
    MED-B  ordinary    price 1000   reorder 5     stock: b1=12
    CTL-A  controlled  price 9000   reorder 2     stock: b1=20
    prescribers allowed: PRB-001, PRB-002   (PRB-999 is NOT allowed)
"""
from pharmacy.data.repository import Repository
from pharmacy.domain import Branch, Prescription, make_medicine
from pharmacy.services.dispensing_service import DispensingService

MAIN = 1
SATELLITE = 2
ALLOWED = "PRB-001"
UNLISTED = "PRB-999"   # a non-empty string that is not on the allow-list


def make_repo(path=":memory:"):
    repo = Repository(path)
    with repo.transaction():
        repo.add_branch("Main Campus")
        repo.add_branch("Satellite Clinic")
        repo.add_medicine(make_medicine("MED-A", "Fictional Ordinary A", 500, 5, False))
        repo.add_medicine(make_medicine("MED-B", "Fictional Ordinary B", 1000, 5, False))
        repo.add_medicine(make_medicine("CTL-A", "Fictional Controlled A", 9000, 2, True))
        repo.add_stock(MAIN, "MED-A", 100)
        repo.add_stock(SATELLITE, "MED-A", 10)
        repo.add_stock(MAIN, "MED-B", 12)
        repo.add_stock(MAIN, "CTL-A", 20)
        # the repository has no add_prescriber(), so the test data is inserted directly
        repo.conn.execute("INSERT INTO prescribers (code, name) VALUES ('PRB-001', 'Dr Fictional One')")
        repo.conn.execute("INSERT INTO prescribers (code, name) VALUES ('PRB-002', 'Dr Fictional Two')")
    return repo


def make_service(path=":memory:"):
    repo = make_repo(path)
    return DispensingService(repo), repo


def new_prescription(service, lines, prescriber=ALLOWED, branch_id=MAIN, patient="PT-9001"):
    """Build, validate and save a prescription. lines = [(code, qty), ...]. Returns its id."""
    rx = Prescription(patient, Branch("Main Campus", id=branch_id), prescriber)
    for code, qty in lines:
        rx.add_line(code, qty)
    return service.create_prescription(rx)


def snapshot(repo):
    """Everything dispensing can change: all stock rows and all prescription statuses."""
    stock = repo.conn.execute(
        "SELECT branch_id, medicine_code, quantity FROM stock ORDER BY 1, 2").fetchall()
    status = repo.conn.execute("SELECT id, status FROM prescriptions ORDER BY id").fetchall()
    return [tuple(r) for r in stock], [tuple(r) for r in status]
