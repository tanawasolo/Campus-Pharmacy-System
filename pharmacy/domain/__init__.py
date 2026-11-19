"""Public surface of the pharmacy domain layer.

Other layers import from here, for example:

    from pharmacy.domain import Medicine, Branch, Prescription, PharmacyError

The modules depend on each other in this order: exceptions, medicine, branch,
stock_item, prescription, prescriber_registry. None of them imports this
package's __init__ back, so there are no circular imports.
"""

from pharmacy.domain.branch import Branch
from pharmacy.domain.exceptions import (
    AlreadyDispensedError,
    CancelledPrescriptionError,
    DuplicateMedicineError,
    EmptyPrescriptionError,
    InsufficientStockError,
    InvalidPriceError,
    InvalidQuantityError,
    InvalidReorderLevelError,
    PharmacyError,
    UnauthorisedPrescriberError,
)
from pharmacy.domain.medicine import (
    ControlledMedicine,
    Medicine,
    OrdinaryMedicine,
    make_medicine,
)
from pharmacy.domain.prescriber_registry import PrescriberRegistry
from pharmacy.domain.prescription import (
    CANCELLED,
    DISPENSED,
    PENDING,
    Prescription,
    PrescriptionLine,
)
from pharmacy.domain.stock_item import StockItem

__all__ = [
    "PharmacyError",
    "InvalidPriceError",
    "InvalidReorderLevelError",
    "InvalidQuantityError",
    "InsufficientStockError",
    "UnauthorisedPrescriberError",
    "AlreadyDispensedError",
    "CancelledPrescriptionError",
    "DuplicateMedicineError",
    "EmptyPrescriptionError",
    "Medicine",
    "OrdinaryMedicine",
    "ControlledMedicine",
    "make_medicine",
    "Branch",
    "StockItem",
    "PENDING",
    "DISPENSED",
    "CANCELLED",
    "PrescriptionLine",
    "Prescription",
    "PrescriberRegistry",
]