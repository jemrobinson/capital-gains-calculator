from .transaction import Transaction


class Purchase(Transaction):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = "BOUGHT"

    @property
    def subtotal(self):
        return self.subtotal_
