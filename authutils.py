"""Helps in authentication related tasks."""
from bcrypt import gensalt, hashpw, checkpw
from flask import session, redirect, url_for, flash
from functools import wraps


def require_login(func: object) -> object:
    """Protect the decorated view function from unauthorized access."""

    @wraps(func)
    def wrapper(*args, **kwargs) -> 'function | Redirect':
        """Check if a user is 'logged_in'."""
        # decorated function 'func' is invoked only if the user is logged in. 
        if 'logged_in' in session:
            return func(*args, **kwargs)
        else:
            # Redirect to login function if not logged_in
            flash('Please login before accessing this page.')
            return redirect(url_for('login'))

    return wrapper


def get_hash(plain: str) -> str:
    """Generate hash for a plain string after salting it."""
    salt = gensalt()
    return hashpw(plain.encode('utf-8'), salt).decode('utf-8')


def check_hash(plain: str, hash: str) -> bool:
    """Check if a given hash can equal a plain string if it is hashed."""
    return checkpw(plain.encode('utf-8'), hash.encode('utf-8'))