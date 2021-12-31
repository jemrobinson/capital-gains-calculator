# Standard library imports
import copy
import logging

# Third party imports
from moneyed import GBP

# Local imports
from .disposal import Disposal, BedAndBreakfast
from .excess_reportable_income import ExcessReportableIncome
from .pooled_purchase import PooledPurchase
from .purchase import Purchase
from .reconcile import reconcile, exchange
from .sale import Sale


class Security:
    def __init__(self, symbol, name, currency=GBP):
        self.symbol = symbol
        self.name = name
        self.currency = currency
        self.transactions = []
        self.events = []

    def __repr__(self):
        return f"Security({self.name} [{self.symbol}])"

    def __str__(self):
        output = repr(self) + "\n"
        for transaction in self.transactions:
            output += f"   {transaction}\n"
        return output

    def add_transactions(self, df):
        for _, transaction in df.iterrows():
            if transaction.Type.lower() == "buy":
                self.transactions.append(
                    Purchase(
                        transaction.Date,
                        self.currency,
                        transaction.Shares,
                        transaction.Amount,
                        transaction.Fees,
                        transaction.Taxes,
                        transaction.Note,
                    )
                )
            elif transaction.Type.lower() == "sell":
                self.transactions.append(
                    Sale(
                        transaction.Date,
                        self.currency,
                        transaction.Shares,
                        transaction.Amount,
                        transaction.Fees,
                        transaction.Taxes,
                        transaction.Note,
                    )
                )
            elif (
                transaction.Note
                and str(transaction.Note).lower() == "excess reportable income"
            ):
                self.transactions.append(
                    ExcessReportableIncome(
                        transaction.Date, self.currency, transaction.Amount
                    )
                )
            elif transaction.Type.lower() in [
                "fees refund",
                "dividend",
                "dividends",
                "fees_refund",
            ]:
                pass
            else:
                raise ValueError(f"Unknown transaction!\n{transaction}")
        self.resolve_transactions()

    @property
    def disposals(self):
        return [e for e in self.events if isinstance(e[0], Disposal)]

    def resolve_transactions(self):
        # Sort transactions and separate into purchases and sales
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
            purchases_ = list(filter(lambda p: p.date < sale.date, purchases))
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
                lambda ptuple: 0 <= (ptuple[1].date - sale.date).days <= 30,
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
        self.events = []
        pool = PooledPurchase(self.currency)
        for transaction in sorted(transactions, key=lambda t: t.datetime):
            logging.debug(
                f"Starting a transaction with {pool.units} shares in the pool"
            )
            pool = copy.deepcopy(pool)
            if isinstance(transaction, ExcessReportableIncome):
                logging.debug(
                    f"=> Found an ExcessReportableIncome event on {transaction.date}:"
                )
                logging.debug(f"  {transaction}")
                pool.add_purchase(transaction)
                self.events.append((transaction, pool))
            elif isinstance(transaction, Purchase):
                logging.debug(f"=> Found a Purchase on {transaction.date}:")
                logging.debug(f"  {transaction}")
                pool.add_purchase(transaction)
                self.events.append((transaction, pool))
            elif isinstance(transaction, BedAndBreakfast):
                logging.debug(f"=> Found a BedAndBreakfast on {transaction.date}:")
                logging.debug(f"  {transaction}")
                pool.add_bed_and_breakfast(transaction)
                self.events.append((transaction, pool))
            elif isinstance(transaction, Disposal):
                logging.debug(f"=> Found a Disposal on {transaction.date}:")
                logging.debug(f"  {transaction}")
                pool.add_disposal(transaction)
                self.events.append((transaction, pool))
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
                self.events.append((disposal, pool))
            else:
                raise ValueError(
                    f"Unknown event of type {type(transaction).__name__}:\n {transaction}"
                )
            logging.debug(f"Ending transaction with {pool.units} shares in the pool")

    def report(self):
        logging.info(f"{self.name:88s} {f'({self.symbol})':>18s}")
        for transaction, pool in sorted(self.events, key=lambda e: e[0].datetime):
            date_prefix = f"  {transaction.date}:"
            date_spacing = " " * len(date_prefix)
            logging.debug(f"Processing event of type {type(transaction).__name__}:")
            logging.debug(f"=> {str(transaction)}")
            if transaction.is_null:
                logging.debug(f"Skipping transaction {str(transaction)}")
                continue
            if isinstance(transaction, ExcessReportableIncome):
                logging.info(
                    f"{date_prefix} {f'ERI of {transaction.units} shares at {transaction.subtotal} plus {transaction.charges} costs':52} {str(transaction.total):>18s}"
                )
            elif isinstance(transaction, Purchase):
                logging.info(
                    f"{date_prefix} {f'Bought {transaction.units} shares at {transaction.subtotal} plus {transaction.charges} costs':52} {str(transaction.total):>18s}"
                )
            elif isinstance(transaction, BedAndBreakfast):
                logging.info(
                    f"{date_prefix} {f'B&B: bought {transaction.units} shares at {transaction.unit_price_bought}':52} {str(transaction.purchase_total):>18}"
                )
                logging.info(
                    f"{date_spacing} {f'B&B: sold {transaction.units} shares at {transaction.unit_price_sold}':52} {str(transaction.sale_total):>18}"
                )
                logging.info(
                    f"{date_spacing} {'Resulting gain':74} {str(transaction.gain):>18}"
                )
            elif isinstance(transaction, Disposal):
                logging.info(
                    f"{date_prefix} {f'Sold {transaction.units} shares at {transaction.unit_price_sold} each':52} {str(transaction.sale_total):>18}"
                )
                logging.info(
                    f"{date_spacing} {f'Cost of {transaction.units} shares from pool was {transaction.unit_price_bought} each':52} {str(transaction.purchase_total):>18}"
                )
                logging.info(
                    f"{date_spacing} {'Resulting gain':74} {str(transaction.gain):>18}"
                )
            elif isinstance(transaction, Sale):
                logging.info(
                    f"{date_prefix} {f'Sold {transaction.units} shares at {transaction.subtotal} plus {transaction.charges} costs':52} {str(transaction.total):>18s}"
                )
            else:
                raise ValueError(
                    f"Unknown event of type {type(transaction).__name__}:\n {transaction}"
                )
            logging.info(
                f"{date_spacing} Pool: {pool.units} shares, cost {str(pool.total)}"
            )
