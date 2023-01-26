"""Definition of the Dividend class"""
# Third-party imports
from moneyed import Money

# Local imports
from .transaction import Transaction


class Dividend(Transaction):
    """Transaction where a dividend is paid by a security"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type: str = "Dividend"

    @property
    def subtotal(self) -> Money:
        return self.subtotal_
