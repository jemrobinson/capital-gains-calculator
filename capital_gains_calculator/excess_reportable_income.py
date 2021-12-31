# Local imports
from .purchase import Purchase


class ExcessReportableIncome(Purchase):
    def __init__(self, date_time, currency, amount, **kwargs):
        super().__init__(
            date_time=date_time,
            currency=currency,
            subtotal=amount,
            units=0,
            fees=0,
            taxes=0,
            **kwargs
        )
        self.type = "ERI"
