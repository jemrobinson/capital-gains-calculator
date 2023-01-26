"""Definition of the Sale class"""
# Third-party imports
from moneyed import Money

# Local imports
from .transaction import Transaction


class Sale(Transaction):
    """Transaction where a security is sold"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type: str = "Sold"

    @property
    def subtotal(self) -> Money:
        return -self.subtotal_
