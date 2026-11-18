"""Role A: Medicine hierarchy. Fill in every TODO yourself."""
from abc import ABC, abstractmethod

from pharmacy.domain.exceptions import InvalidPriceError, InvalidReorderLevelError


class Medicine(ABC):
    """Abstract base. Properties must validate in their setters."""

    def __init__(self, code, name, unit_price, reorder_level):
        # TODO: assign through the properties so validation runs in the constructor
        raise NotImplementedError

    # TODO: properties code, name, unit_price (> 0), reorder_level (int >= 0)
    #       with validating setters raising InvalidPriceError / InvalidReorderLevelError

    @abstractmethod
    def requires_authorisation(self) -> bool:
        """True if dispensing needs an allow-listed prescriber."""

    def category(self) -> str:
        # TODO: override in subclasses ("Ordinary" / "Controlled")
        raise NotImplementedError


class OrdinaryMedicine(Medicine):
    def requires_authorisation(self) -> bool:
        raise NotImplementedError  # TODO


class ControlledMedicine(Medicine):
    def requires_authorisation(self) -> bool:
        raise NotImplementedError  # TODO
