"""Definition of the Security class"""
# Standard library imports
import copy
import logging
from datetime import date
from typing import List, Tuple

# Third party imports
from moneyed import Currency

# Local imports
from .reconcile import exchange, reconcile
from .transactions import (
    BedAndBreakfast,
    Disposal,
    Dividend,
    ExcessReportableIncome,
    PooledPurchase,
    Purchase,
    Sale,
    ScripDividend,
    Transaction,
)


class Security:
    """Representation of a single security and associated transactions"""

    def __init__(self, symbol: str, name: str, currency: Currency):
        self.symbol = symbol
        self.name = name
        self.currency = currency
        self.transactions: List[Transaction] = []
        self.events_: List[Tuple[Transaction, PooledPurchase]] = []

    def __repr__(self):
        return f"Security({self.name} [{self.symbol}])"

    def __str__(self):
        output = repr(self) + "\n"
        for transaction in self.transactions:
            output += f"   {transaction}\n"
        return output

    def add_transactions(self, transactions: List[Transaction]) -> None:
        """Add new transactions then resolve them together with existing transactions"""
        # Add new transactions
        self.transactions += transactions
        # Resolve all transactions
        self.resolve_transactions()

    @property
    def disposals(self) -> List[Tuple[Transaction, PooledPurchase]]:
        """List of all disposals"""
        return [e for e in self.events if isinstance(e[0], Disposal)]

    @property
    def events(self) -> List[Tuple[Transaction, PooledPurchase]]:
        """Return sorted events"""
        self.events_.sort(key=lambda e: e[0].datetime)
        return self.events_

    def is_held(self, start_date: date = None, end_date: date = None) -> bool:
        """Was this security held between the specified dates (inclusive)?"""
        # Check whether any units were held on the start date
        events_before = [
            event for event in self.events if event[0].datetime.date() < start_date
        ]
        if events_before:
            if events_before[-1][1].units > 0:
                return True
        # Check whether any units were held during the year
        for event in filter(
            lambda e: start_date <= e[0].datetime.date() <= end_date, self.events
        ):
            if event[1].units > 0:
                return True
        return False

    def report_capital_gains(
        self, start_date: date = None, end_date: date = None
    ) -> None:
        """Produce a capital gains report"""
        # If there are no disposals in the time range there can be no capital gains
        if not any(start_date <= d[0].date <= end_date for d in self.disposals):
            return

        # Generate the capital gains report
        logging.info(f"{self.name:88s} {f'({self.symbol})':>18s}")
        for transaction, pool in self.events:
            # Ignore any transactions after the end of the tax year
            if transaction.datetime.date() > end_date:
                continue
            date_prefix = f"  {transaction.date}:"
            date_spacing = " " * len(date_prefix)
            logging.debug(f"Processing event of type {type(transaction).__name__}:")
            logging.debug(f"=> {str(transaction)}")
            if transaction.is_null:
                logging.debug(f"Skipping transaction {str(transaction)}")
                continue
            if isinstance(transaction, ExcessReportableIncome):
                logging.info(
                    f"{date_prefix} {f'ERI of {transaction.units} shares @ {transaction.subtotal} plus {transaction.charges} costs':52} {str(transaction.total):>18s}"
                )
            elif isinstance(transaction, ScripDividend):
                logging.info(
                    f"{date_prefix} {f'Scrip dividend of {transaction.units} shares':52} {str(transaction.total):>18s}"
                )
            elif isinstance(transaction, Purchase):
                logging.info(
                    f"{date_prefix} {f'Bought {transaction.units} shares for {transaction.subtotal} plus {transaction.charges} costs':52} {str(transaction.total):>18s}"
                )
            elif isinstance(transaction, BedAndBreakfast):
                logging.info(
                    f"{date_prefix} {f'B&B: bought {transaction.units} shares @ {transaction.unit_price_bought}':52} {str(transaction.purchase_total):>18}"
                )
                logging.info(
                    f"{date_spacing} {f'B&B: sold {transaction.units} shares @ {transaction.unit_price_sold}':52} {str(transaction.sale_total):>18}"
                )
                if start_date <= transaction.datetime.date() <= end_date:
                    logging.info(
                        f"{date_spacing} {'Resulting gain':74} {str(transaction.gain):>18}"
                    )
                else:
                    logging.info(
                        f"{date_spacing} Resulting gain applies to another tax year"
                    )
            elif isinstance(transaction, Disposal):
                logging.info(
                    f"{date_prefix} {f'Sold {transaction.units} shares @ {transaction.unit_price_sold} each':52} {str(transaction.sale_total):>18}"
                )
                if start_date <= transaction.datetime.date() <= end_date:
                    logging.info(
                        f"{date_spacing} {f'Cost of {transaction.units} shares from pool @ {transaction.unit_price_bought} each':52} {str(transaction.purchase_total):>18}"
                    )
                    logging.info(
                        f"{date_spacing} {'Resulting gain':74} {str(transaction.gain):>18}"
                    )
                else:
                    logging.info(
                        f"{date_spacing} Resulting gain applies to another tax year"
                    )
            elif isinstance(transaction, Sale):
                logging.info(
                    f"{date_prefix} {f'Sold {transaction.units} shares @ {transaction.subtotal} plus {transaction.charges} costs':52} {str(transaction.total):>18s}"
                )
            else:
                raise ValueError(
                    f"Unknown event of type {type(transaction).__name__}:\n {transaction}"
                )
            logging.info(
                f"{date_spacing} Pool: {pool.units} shares @ {pool.unit_price_inc} each, cost {str(pool.total)} "
            )

    def report_dividends(self, start_date: date = None, end_date: date = None) -> None:
        """Produce a dividends report"""
        # Load all dividend transactions between the dates
        dividends = [
            t
            for t in self.transactions
            if (start_date <= t.datetime.date() <= end_date) and isinstance(t, Dividend)
        ]
        # If there are dividends then log them
        if dividends:
            logging.info(f"{self.name:88s} {f'({self.symbol})':>18s}")
            for dividend in dividends:
                logging.info(
                    f"  {dividend.date}: {f'Dividend for {dividend.units} shares @ {dividend.unit_price} each':52} {str(dividend.total):>18}"
                )

    def resolve_transactions(self) -> None:
        """Resolve all transactions in the list"""
        # Sort transactions and separate into purchases and sales
        logging.debug(
            f"Resolving {len(self.transactions)} transactions for {self.name} ({self.symbol})"
        )
        sorted_transactions = sorted(self.transactions, key=lambda t: t.datetime)
        purchases = list(filter(lambda t: isinstance(t, Purchase), sorted_transactions))
        sales = list(filter(lambda t: isinstance(t, Sale), sorted_transactions))
        disposals = []

        # Under HS285 share reorganisations should count the new shares as being bought at the same time as the old shares
        # There may be a small additional capital gain
        for idx_sale, sale in [
            s for s in enumerate(sales) if "exchange" in s[1].note.lower()
        ]:
            logging.debug(
                "Combining sale with previous purchases as this is an exchange under HS285:"
            )
            logging.debug(f"  {sale}")
            purchases_ = list(filter(lambda p, d=sale.date: p.date < d, purchases))
            purchase_, sale_, disposal = exchange(purchases_, sale)
            logging.debug(f"  {purchases_}")
            sales[idx_sale] = sale_
            disposals.append(disposal)
            logging.debug("Result:")
            logging.debug(f"  {purchase_}")
            logging.debug(f"  {sale_}")
            logging.debug(f"  {disposal}")

        # Consider whether each sale must be reconciled against purchases according to HS284
        # First consider same day purchases followed by bed-and-breakfasting against any purchase within 30 days
        # Date-ordering any purchases between 0 and 30 days following the sale will automatically apply this
        for idx_sale, sale in enumerate(sales):
            for idx_purchase, purchase in filter(
                lambda ptuple, d=sale.date: 0 <= (ptuple[1].date - d).days <= 30,
                enumerate(purchases),
            ):
                logging.debug("Combining purchase and sale under HS284:")
                logging.debug(f"  {purchase}")
                logging.debug(f"  {sale}")
                purchase_, sale_, disposal = reconcile(purchase, sale)
                disposals.append(BedAndBreakfast(disposal))
                purchases[idx_purchase] = purchase_
                sales[idx_sale] = sale_
                logging.debug("Result:")
                logging.debug(f"  {purchase_}")
                logging.debug(f"  {sale_}")
                logging.debug(f"  {disposal}")
        transactions = [t for t in purchases + sales + disposals if t]

        # Each remaining sale can be converted into a disposal against the existing pool
        self.events_ = []
        pool = PooledPurchase(self.currency)
        for transaction in sorted(transactions, key=lambda t: t.datetime):
            logging.debug(
                f"Starting a transaction with {pool.units} shares in the pool"
            )
            pool = copy.deepcopy(pool)
            if isinstance(transaction, Purchase):
                logging.debug(
                    f"=> Found a {type(transaction).__name__} on {transaction.date}:"
                )
                logging.debug(f"  {transaction}")
                pool.add_purchase(transaction)
                self.events.append((transaction, pool))
            elif isinstance(transaction, BedAndBreakfast):
                logging.debug(f"=> Found a BedAndBreakfast on {transaction.date}:")
                logging.debug(f"  {transaction}")
                pool.add_bed_and_breakfast(transaction)
                self.events_.append((transaction, pool))
            elif isinstance(transaction, Disposal):
                logging.debug(f"=> Found a Disposal on {transaction.date}:")
                logging.debug(f"  {transaction}")
                pool.add_disposal(transaction)
                self.events_.append((transaction, pool))
            elif isinstance(transaction, Sale):
                logging.debug(f"=> Found a Sale on {transaction.date}:")
                logging.debug(f"  {transaction}")
                logging.debug("... reconciling against pool to give:")
                purchase, sale, disposal = reconcile(pool, transaction)
                logging.debug(f"  {purchase}")
                logging.debug(f"  {sale}")
                logging.debug(f"  {disposal}")
                if sale.total:
                    raise ValueError(f"Found an unexpected Sale {sale}")
                pool.add_disposal(disposal)
                self.events_.append((disposal, pool))
            else:
                raise ValueError(
                    f"Unknown event of type {type(transaction).__name__}:\n {transaction}"
                )
            logging.debug(f"Ending transaction with {pool.units} shares in the pool")
