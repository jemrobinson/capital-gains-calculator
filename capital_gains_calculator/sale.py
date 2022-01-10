"""Definition of the Sale class"""
# Local imports
from .transaction import Transaction


class Sale(Transaction):
    """Transaction where a security is sold"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = "SOLD"

    @property
    def subtotal(self):
        return -self.subtotal_
