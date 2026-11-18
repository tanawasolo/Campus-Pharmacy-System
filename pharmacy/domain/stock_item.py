"""Role A: stock quantity of one medicine at one branch."""
from pharmacy.domain.exceptions import InsufficientStockError, InvalidQuantityError


class StockItem:
    def __init__(self, branch_id, medicine_code, quantity=0):
        # TODO: store fields; quantity through the validating property
        raise NotImplementedError

    # TODO: quantity property (never negative)

    def add(self, n):
        """TODO: reject n <= 0 with InvalidQuantityError, then increase."""
        raise NotImplementedError

    def remove(self, n):
        """TODO: raise InsufficientStockError if n > quantity, else decrease."""
        raise NotImplementedError

    def is_low(self, reorder_level) -> bool:
        """TODO: quantity <= reorder_level."""
        raise NotImplementedError
