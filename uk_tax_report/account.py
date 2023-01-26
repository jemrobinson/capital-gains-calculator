"""Definition of the Account class"""
# Standard library imports
import logging
from datetime import date
from typing import List, Optional

# Local imports
from .converters import as_currency
from .readers import DataFile
from .security import Security
from .transactions import Transaction


class Account:
    """Account containing several transactions"""

    def __init__(self, name: str, currency: str, data: Optional[DataFile] = None):
        self.name = name
        self.currency = as_currency(currency)
        if data:
            self.securities = [
                Security(
                    symbol=security_tuple.Symbol,
                    name=security_tuple.Security,
                    currency=self.currency,
                )
                for security_tuple in data.securities[self.name]
            ]
            for security in self.securities:
                security.add_transactions(
                    data.get_transaction_list(self.name, security.name, self.currency)
                )

    def __add__(self, other: "Account") -> "Account":
        if self.currency != other.currency:
            raise ValueError(
                f"Cannot add account '{self.name}' with currency {self.currency} to account '{other.name}' with currency {other.currency}"
            )
        output = Account(f"{self.name}-{other.name}", self.currency)
        output.securities = [
            Security(old.symbol, old.name, self.currency)
            for old in set(self.securities + other.securities)
        ]
        for security in output.securities:
            for existing_security in self.securities + other.securities:
                if existing_security.name == security.name:
                    security.add_transactions(existing_security.transactions)
        return output

    def __radd__(self, other):
        if not isinstance(other, Account):
            return self
        return other + self

    @property
    def taxable_securities(self) -> List[Security]:
        return [s for s in self.securities if not "VCT" in s.name]

    @property
    def transactions(self) -> List[Transaction]:
        """List of transactions in this account"""
        return sum([security.transactions for security in self.securities], [])

    def holdings(self, start_date: date, end_date: date) -> List[Security]:
        """List of securities held between these dates"""
        return [
            security
            for security in self.securities
            if security.is_held(start_date, end_date)
        ]

    def report(self, start_date: date, end_date: date):
        """Report tax summary for this account"""
        # Restrict to specified accounts
        logging.info(
            f"Account '{self.name}' has {len(self.transactions)} transactions across {len(self.securities)} securities"
        )

        # Holdings
        logging.info(
            f"Listing holdings during UK tax year {start_date.year}-{end_date.year}..."
        )
        for security in self.holdings(start_date, end_date):
            logging.info(f"  {f'[{security.symbol}]':15} {security.name}")

        # Capital gains
        logging.info(
            f"Looking for capital gains during UK tax year {start_date.year}-{end_date.year}..."
        )
        for security in self.taxable_securities:
            security.report_capital_gains(start_date, end_date)

        # Dividends
        logging.info(
            f"Looking for dividends during UK tax year {start_date.year}-{end_date.year}..."
        )
        for security in self.taxable_securities:
            security.report_dividends(start_date, end_date)

    def __str__(self) -> str:
        return f"Account '{self.name}' has {len(self.securities)} securities"
