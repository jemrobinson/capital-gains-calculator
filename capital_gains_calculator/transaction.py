"""Definition of the Transaction class"""
# Standard library imports
from decimal import Decimal

# Local imports
from .utils import as_money, as_datetime, abs_divide


class Transaction:
    """Transaction where money is exchanged for a security"""

    def __init__(
        self, date_time, currency, units=0, subtotal=0, fees=0, taxes=0, note=""
    ):
        self.datetime = as_datetime(date_time)
        self.currency = currency
        self.units = Decimal(units)
        self.subtotal_ = as_money(subtotal, currency)
        self.fees = as_money(fees, currency)
        self.taxes = as_money(taxes, currency)
        self.note = str(note)
        self.type = None

    @property
    def date(self):
        """Date of transaction"""
        return self.datetime.date()

    @property
    def unit_price(self):
        """Base price paid per unit in this transaction"""
        return abs_divide(self.subtotal, self.units)

    @property
    def unit_fees(self):
        """Fees paid per unit in this transaction"""
        return abs_divide(self.fees, self.units)

    @property
    def unit_taxes(self):
        """Taxes paid per unit in this transaction"""
        return abs_divide(self.taxes, self.units)

    @property
    def unit_price_inc(self):
        """Total price paid per unit in this transaction"""
        return abs_divide(self.total, self.units)

    @property
    def charges(self):
        """Total charges paid in this transaction"""
        return self.fees + self.taxes

    @property
    def subtotal(self):
        """Subtotal must be implemented by child classes"""
        raise NotImplementedError

    @property
    def total(self):
        """Total paid in this transaction"""
        return self.charges + self.subtotal

    @property
    def is_null(self):
        """Whether this is a null transaction"""
        return self.total == self.currency.zero

    def __str__(self):
        return f"Transaction: {self.type:8s} date = {self.date}, units = {self.units}, unit_price = {self.unit_price}, subtotal = {self.subtotal}, fees = {self.fees}, taxes = {self.taxes}, total = {self.total}"
