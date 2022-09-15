"""General utility functions for converting between types"""
# Standard library imports
import datetime
from decimal import InvalidOperation

# Third party imports
from dateutil.parser import parse
from moneyed import Money
from numpy import isnan


def as_money(data, currency):
    """Convert arbitrary data into Money"""
    if isinstance(data, Money):
        return data
    if isnan(float(data)):
        return Money(0, currency)
    return Money(data, currency)


def as_datetime(data):
    """Convert arbitrary data into a datetime"""
    if isinstance(data, datetime.datetime):
        return data
    return parse(data)


def abs_divide(money, number):
    """
    The absolute value of dividing Money by a number.
    Returns 0 if there is an invalid division.
    """
    try:
        result = abs(money / number)
    except (ZeroDivisionError, InvalidOperation):
        result = Money(0, money.currency)
    return result
