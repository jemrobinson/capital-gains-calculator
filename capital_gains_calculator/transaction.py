from decimal import Decimal
from .utils import as_money, as_datetime, abs_divide


class Transaction:
    def __init__(self, date_time, currency, units=0, subtotal=0, fees=0, taxes=0):
        self.datetime = as_datetime(date_time)
        self.currency = currency
        self.units = Decimal(units)
        self.subtotal_ = as_money(subtotal, currency)
        self.fees = as_money(fees, currency)
        self.taxes = as_money(taxes, currency)

    @property
    def date(self):
        return self.datetime.date()

    @property
    def unit_price(self):
        return abs_divide(self.subtotal, self.units)

    @property
    def unit_fees(self):
        return abs_divide(self.fees, self.units)

    @property
    def unit_taxes(self):
        return abs_divide(self.taxes, self.units)

    @property
    def unit_price_inc(self):
        return abs_divide(self.total, self.units)

    @property
    def charges(self):
        return self.fees + self.taxes

    @property
    def subtotal(self):
        raise NotImplementedError

    @property
    def total(self):
        return self.charges + self.subtotal

    def __str__(self):
        return f"Transaction: {self.type:6s} date = {self.date}, units = {self.units}, unit_price = {self.unit_price}, subtotal = {self.subtotal}, fees = {self.fees}, taxes = {self.taxes}, total = {self.total}"
