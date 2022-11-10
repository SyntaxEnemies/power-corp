from bcrypt import gensalt, hashpw, checkpw
from flask import session, redirect, url_for, flash
from functools import wraps


def require_login(func: object) -> object:
    """This Decorator protects the argumented function from unauthorized
    access by 'checking' if the user is authorized"""

    @wraps(func)
    def wrapper(*args, **kwargs) -> 'function | Redirect':
        """ This decorator wraps extra code that checks if a user is
        'logged_in' around a view function """

        if 'logged_in' in session:        # decorated function 'func' is invoked only if the user is logged in. 
            return func(*args, **kwargs)  # wrapper' must have the sigature as of decorated function as it has to return it.
        else:
            flash('Please login before accessing this page.')
            return redirect(url_for('login'))

    return wrapper # 'check_status' returns the 'wrapper' function's object.


def get_hash(plain: str) -> str:
    salt = gensalt()
    return hashpw(plain.encode('utf-8'), salt).decode('utf-8')


def check_hash(plain: str, hash: str) -> bool:
    return checkpw(plain.encode('utf-8'), hash.encode('utf-8'))
