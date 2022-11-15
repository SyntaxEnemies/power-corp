import mariadb


class UseDatabase():
    def __init__(self, config: dict) -> None:
        self.configuration = config
        # dunder init takes care of all object creation argument(s).

    def __enter__(self) -> 'MariaDB cursor':
        self.conn = mariadb.connect(**self.configuration)
        self.cursor = self.conn.cursor()
        return self.cursor
        # The 'conn' and 'cursor' are prefixed with 'self' 
        # so that they survive for use in 'dunder exit' 

    def __exit__(self, exc_type, exc_value, exc_trace) -> None:
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

        if exc_type:
            raise exc_type(exc_value)
