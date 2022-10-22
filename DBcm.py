import mariadb


class ConnectionError(Exception):
	pass

class CredentialsError(Exception):
	pass

class SQLError(Exception):
	pass


class UseDatabase():
	def __init__(self, config: dict) -> None:
		self.configuration = config
		# dunder init takes care of all object creation argument(s).


	def __enter__(self) -> 'MariaDB cursor':
		try:
			self.conn = mariadb.connect(**self.configuration)
			self.cursor = self.conn.cursor()
			return self.cursor
		# The 'conn' and 'cursor' are prefixed with 'self' 
		# so that they survive for use in 'dunder exit' 

		except mariadb.InterfaceError as err:
			raise ConnectionError(err)

		except mariadb.ProgrammingError as err:
			raise CredentialsError(err)


	def __exit__(self, exc_type, exc_value, exc_trace) -> None:
		self.conn.commit()
		self.cursor.close()
		self.conn.close()

		if exc_type is mariadb.ProgrammingError:
			raise SQLError(exc_value)
		elif exc_type:
			raise exc_type(exc_value)
