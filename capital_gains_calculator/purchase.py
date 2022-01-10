"""Definition of the Purchase class"""
# Local imports
from .transaction import Transaction


class Purchase(Transaction):
    """Transaction where a security is bought"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = "BOUGHT"

    @property
    def subtotal(self):
        return self.subtotal_
