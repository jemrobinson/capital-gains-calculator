import datetime
from decimal import InvalidOperation
from dateutil.parser import parse
from moneyed import Money
from numpy import isnan


def as_money(data, currency):
    if isinstance(data, Money):
        return data
    if isnan(float(data)):
        return Money(0, currency)
    else:
        return Money(data, currency)


def as_datetime(data):
    if isinstance(data, datetime.datetime):
        return data
    return parse(data)


def abs_divide(money, number):
    try:
        result = abs(money / number)
    except (ZeroDivisionError, InvalidOperation):
        result = Money(0, money.currency)
    return result
