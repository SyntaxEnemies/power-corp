"""Functions that provide python interface for DB transactions."""
from main import app

from DBcm import UseDatabase

# Find DB configuration variables in flask config variables (prefix 'DB_')
# Copy them into separate dictionary
dbconfig = {k.removeprefix('DB_').lower(): v for k, v in app.config.items() if k.startswith('DB_')}


def dict_to_sql(columns: list, table: str) -> str:
    """Prepare SQL insert query for table getting columns from list."""
    # Placeholders (%s) to use in prepared query string
    placeholders = ', '.join(['%s'] * len(insert_data))
    columns = ', '.join(columns)

    # Create prepared query string
    template = 'insert into {0} ({1}) values ({2})'
    sql = template.format(table, columns, placeholders)
    return sql


def get_column_names(table: str) -> list:
    """Get column names of a table."""
    with UseDatabase(dbconfig) as cursor:
        # Get table schema
        _SQL = """describe {}""".format(table)
        cursor.execute(_SQL)
        schema = cursor.fetchall()

    columns = []
    # First element of each column's schema is its name
    for row in schema:
        columns.append(row[0])
    return columns


def get_user(uname: str) -> 'dict | None':
    """Fetch a user record that matches the given username.

    Return a dictionary if a user with given username exists in
    the table user_details, else return 'None'.

    The Dictionary is of the form:
    - keys: column names of 'user_details' table
    - values: data of corresponding columns for the given user
    """
    # Array to hold names of columns in 'user_details' table
    keys = get_column_names('user_details')

    with UseDatabase(dbconfig) as cursor:
        # Search for the user
        _SQL = """select * from user_details where username=%s limit 1"""
        cursor.execute(_SQL, (uname,))
        values = cursor.fetchone()

    if not values:
        # If the user doesn't exist
        return None
    else:
        # Return a dict by combining column names and user info lists
        return dict(zip(keys, values))


def add_user(userdata: dict) -> None:
    """Store new user given their data.

    Arguments:
    - userdata:
        - keys: column names of 'user_details' table
        - values: user data to insert in the corresponding columns
    """
    with UseDatabase(dbconfig) as cursor:
        _SQL = dict_to_sql(list(userdata.keys()), 'user_details')
        cursor.execute(_SQL, tuple(userdata.values()))
