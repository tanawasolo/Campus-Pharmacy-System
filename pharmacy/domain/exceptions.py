"""Domain exceptions. Every rule violation raises a subclass of PharmacyError."""


class PharmacyError(Exception):
    """Base class for all pharmacy rule violations."""


class InvalidPriceError(PharmacyError):
    """Unit price must be greater than 0."""


class InvalidReorderLevelError(PharmacyError):
    """Reorder level must be an integer of 0 or more."""


class InvalidQuantityError(PharmacyError):
    """A received or requested quantity must be a whole number greater than 0."""


class InsufficientStockError(PharmacyError):
    """Requested quantity exceeds available stock at the branch."""


class UnauthorisedPrescriberError(PharmacyError):
    """Controlled medicine requires a prescriber on the allow-list."""


class AlreadyDispensedError(PharmacyError):
    """The prescription has already been dispensed."""


class CancelledPrescriptionError(PharmacyError):
    """The prescription has been cancelled."""


class DuplicateMedicineError(PharmacyError):
    """A medicine with this code already exists."""


class EmptyPrescriptionError(PharmacyError):
    """A prescription needs at least one line."""
