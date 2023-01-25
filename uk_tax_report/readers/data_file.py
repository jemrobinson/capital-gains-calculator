"""Definition of the Reader class"""
# Standard library imports
from typing import Set

# Third-party imports
import pandas as pd


class DataFile:
    """Read a PortfolioPerformance data file"""

    def __init__(self):
        self.df_transactions: pd.DataFrame

    @property
    def account_names(self) -> Set[str]:
        """List of account names"""
        return set(self.df_transactions["Cash Account"])

    def account_transactions(self, name) -> pd.DataFrame:
        """DataFrame of account transactions"""
        return self.df_transactions.loc[(self.df_transactions["Cash Account"] == name)]
