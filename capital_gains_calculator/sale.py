# Local imports
from .transaction import Transaction


class Sale(Transaction):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = "SOLD"

    @property
    def subtotal(self):
        return -self.subtotal_
