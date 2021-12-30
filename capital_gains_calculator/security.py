from .sale import Sale
from .purchase import Purchase
from .pooled_purchase import PooledPurchase
from .disposal import Disposal
from moneyed import GBP
from .reconcile import reconcile


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
            if transaction.Type == "Buy":
                self.transactions.append(
                    Purchase(
                        transaction.Date,
                        self.currency,
                        transaction.Shares,
                        transaction.Amount,
                        transaction.Fees,
                        transaction.Taxes,
                    )
                )
            elif transaction.Type == "Sell":
                self.transactions.append(
                    Sale(
                        transaction.Date,
                        self.currency,
                        transaction.Shares,
                        transaction.Amount,
                        transaction.Fees,
                        transaction.Taxes,
                    )
                )
            elif transaction.Note == "Excess reportable income":
                self.transactions.append(
                    Purchase(
                        transaction.Date, self.currency, 0, transaction.Amount, 0, 0
                    )
                )
            elif transaction.Type in ["Fees Refund", "Dividend"]:
                pass
            else:
                raise ValueError(f"Unknown transaction!\n{transaction}")
        self.resolve_transactions()

    @property
    def disposals(self):
        return [e for e in self.events if isinstance(e, Disposal)]

    def resolve_transactions(self):
        # Sort transactions and separate into purchases and sales
        sorted_transactions = sorted(self.transactions, key=lambda t: t.datetime)
        purchases = list(filter(lambda t: isinstance(t, Purchase), sorted_transactions))
        sales = list(filter(lambda t: isinstance(t, Sale), sorted_transactions))
        disposals = []

        # Consider whether each sale must be reconciled against purchases according to HS284
        # First consider same day purchases followed by bed-and-breakfasting against any purchase within 30 days
        # Date-ordering any purchases between 0 and 30 days following the sale will automatically apply this
        for idx_sale, sale in enumerate(sales):
            for idx_purchase, purchase in filter(
                lambda ptuple: 0 <= (ptuple[1].date - sale.date).days <= 30,
                enumerate(purchases),
            ):
                purchase_, sale_, disposal = reconcile(purchase, sale)
                disposals.append(disposal)
                purchases[idx_purchase] = purchase_
                sales[idx_sale] = sale_
        transactions = [t for t in purchases + sales + disposals if t]

        # Each remaining sale can be converted into a disposal against the existing pool
        self.events = []
        pool = PooledPurchase(self.currency)
        for transaction in sorted(transactions, key=lambda t: t.datetime):
            if isinstance(transaction, Purchase):
                pool.add_purchase(transaction)
                self.events.append(transaction)
            if isinstance(transaction, Sale):
                purchase_, sale_, disposal = reconcile(pool, sale)
                pool = PooledPurchase.from_purchase(purchase_, self.currency)
                if sale_.units > 0:
                    raise ValueError(f"Found an unexpected Sale {sale_}")
                self.events.append(disposal)
            if isinstance(transaction, Disposal):
                self.events.append(disposal)

    def report(self):
        print(f"\n{self.name:100s} ({self.symbol})\n")
        pool = PooledPurchase(self.currency)
        for event in sorted(self.events, key=lambda t: t.datetime):
            if isinstance(event, Purchase):
                pool.add_purchase(event)
                details = f"Bought {event.units} shares at {event.subtotal_} plus {event.charges} costs"
                print(f"{event.date}  {details:50} {str(event.total):>20s}")
            elif isinstance(event, Disposal):
                sale_details = f"Sold {event.units} shares at {event.unit_price_sold}"
                print(f"{event.date}  {sale_details:50} {str(event.sale_total):>20}")
                purchase_details = f"Cost of {event.units} shares from pool was {event.unit_price_bought}"
                print(
                    f"            {purchase_details:50} {str(event.purchase_total):>20}"
                )
                print(f"            {'Resulting gain':76} {str(event.gain):>20}")
            else:
                raise ValueError(f"Unknown event {event} of type {type(event)}")
            print(f"            Pool: {pool.units} shares, cost {str(pool.total)}")
