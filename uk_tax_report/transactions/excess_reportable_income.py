"""Definition of the ExcessReportableIncome class"""
# Standard library imports
from datetime import datetime

# Third-party imports
from moneyed import Currency

# Local imports
from .purchase import Purchase


class ExcessReportableIncome(Purchase):
    """Excess reportable income from accumulation shares treated as a purchase of 0 additional shares"""

    def __init__(self, date_time: datetime, currency: Currency, amount, **kwargs):
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
