"""Utility functions related to reconciling transactions"""
# Standard library imports
import logging

# Local imports
from .disposal import Disposal
from .pooled_purchase import PooledPurchase
from .purchase import Purchase
from .sale import Sale


def exchange(transactions, sale):
    """
    Mark a sale as a direct exchange for a set of transactions.

    This usually happens in the case of a stock split where all existing shares
    are exchanged for a different number of new shares. In PortfolioPerformance
    this is most easily modelled as a sale of all shares plus a purchase of new
    ones. In this case, the sale should be an exchange against the sum of all
    previous transactions.
    """
    pool = PooledPurchase(transactions[0].currency)
    for transaction in transactions:
        pool.add_purchase(transaction)
    if pool.units != sale.units:
        raise ValueError(
            f"Unable to match pool with {pool.units} shares against exchange-sale with {sale.units}"
        )
    return reconcile(pool, sale)


def reconcile(purchase, sale):
    """Reconcile a single purchase with a single sale"""
    if not isinstance(purchase, Purchase):
        raise ValueError(f"{purchase} is not a purchase!")
    if not isinstance(sale, Sale):
        raise ValueError(f"{sale} is not a sale!")
    if not sale.currency == purchase.currency:
        raise ValueError(
            f"Currencies {sale.currency} and {purchase.currency} do not match!"
        )
    total_units = abs(purchase.units - sale.units)
    if purchase.units > sale.units:
        # In this case we are selling part of the purchase => the entire sale is consumed
        logging.debug(f"Selling part of the purchase: {sale.units} of {purchase.units}")
        sale_ = Sale(sale.datetime, sale.currency)
        disposal = Disposal(
            sale.datetime,
            sale.currency,
            sale.units,
            purchase.unit_price_inc * sale.units,
            purchase.unit_fees * sale.units,
            purchase.unit_taxes * sale.units,
            abs(sale.total),
            sale.fees,
            sale.taxes,
        )
        f_residual = float(purchase.units - sale.units) / float(purchase.units)
        purchase_residual_fees = f_residual * purchase.fees
        purchase_residual_taxes = f_residual * purchase.taxes
        residual_cost = (
            purchase.total
            - disposal.purchase_total
            - purchase_residual_fees
            - purchase_residual_taxes
        )
        purchase_ = Purchase(
            purchase.datetime,
            purchase.currency,
            total_units,
            residual_cost,
            purchase_residual_fees,
            purchase_residual_taxes,
        )
    elif purchase.units < sale.units:
        # In this case we are selling more than the entire purchase => the entire purchase is consumed
        logging.debug(
            f"Selling more than the entire purchase: {sale.units} of {purchase.units}"
        )
        purchase_ = Purchase(purchase.datetime, purchase.currency)
        disposal = Disposal(
            sale.datetime,
            sale.currency,
            purchase.units,
            purchase.total,
            purchase.fees,
            purchase.taxes,
            sale.unit_price_inc * purchase.units,
            sale.unit_fees * purchase.units,
            sale.unit_taxes * purchase.units,
        )
        f_residual = float(sale.units - purchase.units) / float(sale.units)
        sale_residual_fees = f_residual * sale.fees
        sale_residual_taxes = f_residual * sale.taxes
        residual_cost = (
            sale.total
            + disposal.purchase_total
            - sale_residual_fees
            - sale_residual_taxes
        )
        sale_ = Sale(
            sale.datetime,
            sale.currency,
            total_units,
            residual_cost,
            sale_residual_fees,
            sale_residual_taxes,
        )
    elif purchase.units == sale.units:
        # In this case we are selling the entire purchase => the entire purchase and sale are consumed
        logging.debug(f"Selling the entire purchase: {sale.units} of {purchase.units}")
        sale_ = Sale(sale.datetime, sale.currency)
        purchase_ = Purchase(purchase.datetime, purchase.currency)
        disposal = Disposal(
            sale.datetime,
            sale.currency,
            purchase.units,
            purchase.total,
            purchase.fees,
            purchase.taxes,
            abs(sale.total),
            sale.fees,
            sale.taxes,
        )
    return purchase_, sale_, disposal
