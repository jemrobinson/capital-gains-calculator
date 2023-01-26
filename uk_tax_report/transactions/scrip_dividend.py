"""Definition of the ScripDividend class"""
# Third-party imports
from moneyed import Money

# Local imports
from .purchase import Purchase


class ScripDividend(Purchase):
    """Transaction where security pays a dividend in the form of shares"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type: str = "SCRIP DIV"

    @property
    def subtotal(self) -> Money:
        return self.subtotal_
