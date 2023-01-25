"""Definition of the BedAndBreakfast class"""
# Third-party imports
from moneyed import Money

# Local imports
from .disposal import Disposal


class BedAndBreakfast(Disposal):
    """A disposal where the buying/selling are within 30 days"""

    def __init__(self, disposal: Disposal):
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
    def subtotal(self) -> Money:
        """Subtotal is not a valid property for this class"""
        raise NotImplementedError(
            "Subtotal is not a valid property for the BedAndBreakfast class"
        )
