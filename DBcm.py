"""Context manager for boilerplate and teardown code of DB transaction."""
import mariadb


class UseDatabase():
    """Set up MariaDB cursor to execute queries and cleanup afterwards.

    Attributes:
    - configuration: database configuration
    - conn: MariaDB connection object
    - cursor: MariaDB cursor object
    """

    def __init__(self, config: dict) -> None:
        """Initialize configuration with passed dictionary."""
        # dunder init takes care of all object creation argument(s)
        self.configuration = config

    def __enter__(self) -> 'MariaDB cursor':
        """Connect with DB, initialize cursor and return it."""
        # The 'conn' and 'cursor' are prefixed with 'self'
        # so that they survive for use in 'dunder exit'
        self.conn = mariadb.connect(**self.configuration)
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_value, exc_trace) -> None:
        """Close cursor and connection after commiting transactions."""
        # Check if there was an Exception while executing queries
        if exc_type:
            # print('Rolling back ...')
            self.conn.rollback()
        else:
            self.conn.commit()

        self.cursor.close()
        self.conn.close()

        # Raise Exception that occurred during query execution (if any)
        if exc_type:
            raise exc_type(exc_value)
