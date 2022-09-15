"""Definition of the Disposal and BedAndBreakfast classes"""
# # Third party imports
# from moneyed import Money

# Local imports
from .transaction import Transaction
from .utils import as_money, abs_divide


class Disposal(Transaction):
    """A combined purchase and sale"""

    def __init__(
        self,
        date_time,
        currency,
        units,
        purchase_total,
        purchase_fees,
        purchase_taxes,
        sale_total,
        sale_fees,
        sale_taxes,
    ):
        super().__init__(date_time=date_time, currency=currency, units=units)
        self.purchase_total = as_money(purchase_total, currency)
        self.purchase_fees = as_money(purchase_fees, currency)
        self.purchase_taxes = as_money(purchase_taxes, currency)
        self.sale_total = as_money(sale_total, currency)
        self.sale_fees = as_money(sale_fees, currency)
        self.sale_taxes = as_money(sale_taxes, currency)
        self.type = "DISPOSAL"

    @property
    def subtotal(self):
        """Subtotal is not a valid property for this class"""
        raise NotImplementedError(
            "Subtotal is not a valid property for the Disposal class"
        )
        # return Money(-1, self.currency)

    @property
    def unit_price_sold(self):
        """The unit price at which the units were sold"""
        return abs_divide(self.sale_total, self.units)

    @property
    def unit_price_bought(self):
        """The unit price at which the units were bought"""
        return abs_divide(self.purchase_total, self.units)

    @property
    def gain(self):
        """The capital gain made upon sale"""
        return self.sale_total - self.purchase_total

    @property
    def is_null(self):
        """Whether this is a null transaction"""
        return (self.sale_total == self.currency.zero) and (
            self.purchase_total == self.currency.zero
        )

    def __str__(self):
        return f"Transaction: {self.type:8s} date = {self.date}, units = {self.units}, purchase_total = {self.purchase_total}, sale_total = {self.sale_total}, gain = {self.gain}"


class BedAndBreakfast(Disposal):
    """A disposal where the buying/selling are within 30 days"""

    def __init__(self, disposal):
        super().__init__(
            disposal.datetime,
            disposal.currency,
            disposal.units,
            disposal.purchase_total,
            disposal.purchase_fees,
            disposal.purchase_taxes,
            disposal.sale_total,
            disposal.sale_fees,
            disposal.sale_taxes,
        )

    @property
    def subtotal(self):
        """Subtotal is not a valid property for this class"""
        raise NotImplementedError(
            "Subtotal is not a valid property for the BedAndBreakfast class"
        )
