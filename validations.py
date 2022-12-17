"""Boolean functions for validating input.
An Exception for handling invalid inputs.
"""
from datetime import datetime
from re import fullmatch


class ValidationError(Exception):
    pass


def range_validator(value: int, min: int, max: int) -> bool:
    """Check if a (numeric) value is within min/max constraints."""
    # Both min and max are inclusive.
    if min <= max:
        if value in range(min, max+1):
            return True
        return False

    print("Invalid range constraints.")
    return False


def regex_validator(to_check: str, regex: str) -> bool:
    """Match the given string against given regular expression.

    Ignores trailing whitespace in the string 'to_check'.
    """
    if fullmatch(regex, to_check.rstrip()):
        return True
    return False


def compare_validator(to_check, to_compare) -> bool:
    """Compare a field's value with another field's value."""
    if to_check == to_compare:
        return True
    return False


def type_validator(type: str, valid_types: tuple):
    """Check if a type is one among the given types.

    Parameters:
        - type: given type to validate
        - valid_type: collection of valid types to check from

    Example use:
        You have a 'payment-mode' user input which can be:
            - credit card
            - debit card
            - netbanking
            - store credit
        Then 'payment-mode' and tuple of above options can be passed
        as 'type' and 'valid_types' respectively.
    """
    if type in valid_types:
        return True
    return False


def non_empty(name: str) -> bool:
    """Check if a name has (except from trailing) whitespace."""
    return regex_validator(name, r'.*\S.*')


def is_email(mail_addr: str) -> bool:
    """Check if a email address is valid.

    Uses RFC 5322 as a reference.
    """
    return regex_validator(mail_addr, (r'[a-zA-Z0-9.!#$%&\'*+\/=?^_`{|}~-]+'
                                       r'@[a-zA-Z0-9]'
                                       r'(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])'
                                       r'?(?:\.[a-zA-Z0-9]'
                                       r'(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*'))


def is_decimal_str(num: str, ntotal: int, nprecision: int=0) -> bool:
    """Check if a numeric string represents a decimal number.

    Decimal has fixed number of total and precision digits.
    Precision digits are the ones after a decimal point i.e. period.

    Parameters:
        - num: The numeric string to check
        - ntotal: total number of digits to check in string
        - nprecision: number of digits to check following decimal point

    If nprecision is 0 then decimal point is expected to be absent.
    Non-numeric strings are invalidated.
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


def is_username(username: str) -> bool:
    """Checks if a string is valid password.

    The valid password can only contain:
        - alphabets  ->  a-z
        - numerals   ->  0-9
        - underscore ->  '_'
        - hyphen     ->  '-'
        - period     ->  '.'
    Password must also have at least 4 characters.
    """
    return regex_validator(username, r'[\w\-\.]{4,}')

def is_password(password: str) -> bool:
    """Validates a password string according to set conditions.

    Password string must have:
        - at least 8 characters in total
        - at least 1 lower case alphabet
        - at least 1 upper case alphabet
        - at least 1 numeral
        - at least 1 out of '@', '$', '!', '%', '*', '?', '&' '.'
        - no other type of character other than the 4 listed above

    Character type conditions are checked using a positive lookahead.
    """
    # TODO: Indicate which condition the password doesn't meet.
    return regex_validator(password, r'(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&\.])[A-Za-z\d@$!%*?&\.]{8,}')


def is_correct_date(date: str, date_format: str='%Y-%m-%d') -> bool:
    """Check validity of a date string according to given date format.

    Parameters:
        - date: the string date to be validated
        - format: the date format to check against

    Date format must be complaint with strptime.
    Default date format: 'YYYY-MM-DD'.
    Additionally correctness is determined by checking that the date
    hasn't been passwd by today's date.
    """
    try:
        input_date_obj = datetime.strptime(date, date_format)
    # If date is not in given date format.
    except ValueError as e:
        print(str(e))
        return False

    today_date = datetime.now().strftime(date_format)
    today_date_obj = datetime.strptime(today_date, date_format)

    print('input date: ', input_date_obj, '\ntoday date: ', today_date_obj)
    # Only future and present dates are valid.
    if input_date_obj >= today_date_obj:
        return True
    return False
