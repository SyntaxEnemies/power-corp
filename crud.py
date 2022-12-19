"""Functions that provide python interface for DB transactions."""
from DBcm import UseDatabase
from main import app

# Find DB configuration variables (prefix 'DB_') in flask app config 
# and copy them into separate dictionary
dbconfig = {k.removeprefix('DB_').lower(): v for k, v in app.config.items() if k.startswith('DB_')}


def prepare_insert(columns: list, table: str) -> str:
    """Create prepared SQL insert query with given column names.

    Parameters:
        - table: database table on which insert is performed.
        - columns: list of columns involved in insert.

    Placeholders (%s) are inserted according to number of columns.
    No checking for absence of 'NOT NULL' fields is done.
    """
    # Placeholders (%s) to use in prepared insert query string
    placeholders = ', '.join(['%s'] * len(columns))
    # Convert column names list to a comma separated string.
    columns = ', '.join(columns)

    template = 'insert into {0} ({1}) values ({2})'
    # Create prepared query string by substituting table name, column
    # names and value placeholders.
    sql = template.format(table, columns, placeholders)
    return sql


def get_column_names(table: str) -> list:
    """Get column names of given SQL table."""
    with UseDatabase(dbconfig) as cursor:
        # Get table schema.
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

    Return:
        - user info dict if a user with given username exists
        - None otherwise

    user info dict's:
        - keys: column names of 'user_details' table
        - values: corresponding values for fields of the found record
    """
    # Array to hold names of columns in 'user_details' table.
    keys = get_column_names('user_details')

    with UseDatabase(dbconfig) as cursor:
        # Search for the given username.
        _SQL = """select * from user_details where username=%s limit 1"""
        cursor.execute(_SQL, (uname,))
        values = cursor.fetchone()

    if not values:
        # If the user doesn't exist.
        return None
    else:
        # Return a dict by combining column names and field values of
        # found record in DB.
        return dict(zip(keys, values))


def add_user(basic_data: dict, card_data: dict) -> None:
    """Store a new user given their data.

    Arguments:
    - basic_data: dict inserted as record into 'user_details' table
    - card_data: credit/debit card record for the new user (inserted
                 into 'card_details' table)

    Both database insertions are atomic.
    """
    with UseDatabase(dbconfig) as cursor:
        # Add basic user data into 'user_details' table
        _SQL = prepare_insert(list(basic_data.keys()), 'user_details')
        cursor.execute(_SQL, tuple(basic_data.values()))

        # cursor.lastrowid is value of last auto incremented item in DB
        # It will equal the id of the user just inserted in above query.
        newuser_id = cursor.lastrowid

        # Add new user's id to card_data before inserting as it is
        # required as foreign key when inserting their card details.
        card_data['uid'] = newuser_id
        _SQL = prepare_insert(list(card_data.keys()), 'card_details')
        cursor.execute(_SQL, tuple(card_data.values()))
