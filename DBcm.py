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
        self.configuration = config
        # dunder init takes care of all object creation argument(s).

    def __enter__(self) -> 'MariaDB cursor':
        """Connect with DB, initialize cursor and return it."""
        self.conn = mariadb.connect(**self.configuration)
        self.cursor = self.conn.cursor()
        return self.cursor
        # The 'conn' and 'cursor' are prefixed with 'self' 
        # so that they survive for use in 'dunder exit' 

    def __exit__(self, exc_type, exc_value, exc_trace) -> None:
        """Close cursor and connection after commiting transactions."""
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

        if exc_type:
            raise exc_type(exc_value)
