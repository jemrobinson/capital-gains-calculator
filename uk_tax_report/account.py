"""Definition of the Account class"""
# Standard library imports
import logging
from datetime import date
from typing import List

# Third-party imports
import pandas as pd

# Local imports
from .security import Security
from .transaction import Transaction


class Account:
    """Account containing several transactions"""

    def __init__(self, name: str, df_transactions: pd.DataFrame):
        self.name = name
        account_transactions = df_transactions.loc[
            (df_transactions["Cash Account"] == name)
        ]
        security_tuples = sorted(
            set(
                account_transactions[["ISIN", "Symbol", "Security"]].itertuples(
                    index=False
                )
            ),
            key=lambda t: t.Security.lower(),
        )
        self.securities = [
            Security(symbol=security_tuple.Symbol, name=security_tuple.Security)
            for security_tuple in security_tuples
        ]
        for security in self.securities:
            security.add_transactions(
                account_transactions.loc[
                    (account_transactions["Security"] == security.name)
                ]
            )

    @property
    def transactions(self) -> List[Transaction]:
        """List of transactions in this account"""
        return sum([security.transactions for security in self.securities], [])

    def report(self, start_date: date, end_date: date):
        """Report tax summary for this account"""
        # Restrict to specified accounts
        logging.info(
            f"Account '{self.name}' has {len(self.transactions)} transactions across {len(self.securities)} securities"
        )

        # Capital gains
        logging.info(
            f"Looking for capital gains during UK tax year {start_date.year}-{end_date.year}..."
        )
        for security in self.securities:
            security.report_capital_gains(start_date, end_date)

    def __str__(self) -> str:
        return f"Account '{self.name}' has {len(self.securities)} securities"
