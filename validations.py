import re


class ValidationError(Exception):
    pass


def range_validator(value: int, min: int, max: int) -> bool:
    """Check if given value is """
    # Both min and max are inclusive.
    if min <= max:
        if value in range(min, max+1):
            return True
        return False

    print("Invalid range constraints.")
    return False


def regex_validator(to_check: str, regex: str) -> bool:
    """Match the given string against given regular expression"""
    if re.fullmatch(regex, to_check.rstrip()):
        return True
    return False


def compare_validator(to_check, to_compare) -> bool:
    """Check if given value is equal """
    if to_check == to_compare:
        return True
    return False


def type_validator(to_check: str, valid_types: tuple):
    """Check if a value is one of the given types."""
    if to_check in valid_types:
        return True
    return False


def has_whites(name: str) -> bool:
    """Check if a name has (except from trailing) whitespace."""
    if regex_validator(name.rstrip(), r'.*\s.*'):
        return True
    return False


def isemail(mail_addr: str) -> bool:
    """Check if a email address is valid."""
    if regex_validator(mail_addr, (r'[a-zA-Z0-9.!#$%&\'*+\/=?^_`{|}~-]+'
                                   r'@[a-zA-Z0-9]'
                                   r'(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])'
                                   r'?(?:\.[a-zA-Z0-9]'
                                   r'(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*')):
        return True
    return False


def is_decimal_str(num: str, ntotal: int, nprecision: int=0) -> bool:
    """Check if a numeric string is a decimal string.
    Decimal has fixed number of total and precision digits.

    Parameters:
    - num: The numeric string to check
    - ntotal: total number of digits to check in string
    - nprecision: number of digits to check following decimal point

    If nprecision is 0 then decimal point is expected to be absent.
    """
    if '.' in num:
        # If there are precision digits but nprecision is zero.
        if not nprecision:
            return False

        # Check number of digits in whole and fractional part.
        whole, fraction = num.split('.')
        nwhole = ntotal - nprecision
        if (whole.isnumeric() and len(whole) == nwhole
                and fraction.isnumeric() and len(fraction) == nprecision):
            return True
        return False

    # If there are no precision digits but nprecision is non zero.
    if nprecision:
        return False

    # No precision digits, validation reduces to checking ntotal only.
    if (num.isnumeric() and len(num) == ntotal):
        return True
    return False
