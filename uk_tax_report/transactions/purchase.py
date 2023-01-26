"""Definition of the Purchase class"""
# Third-party imports
from moneyed import Money

# Local imports
from .transaction import Transaction


class Purchase(Transaction):
    """Transaction where a security is bought"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type: str = "Bought"

    @property
    def subtotal(self) -> Money:
        return self.subtotal_
