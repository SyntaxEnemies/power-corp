from DBcm import UseDatabase
from main import app

# Load database configuration into dbconfig dict
dbconfig = {k[3:].lower(): v for k, v in app.config.items() if k.startswith('DB_')}

def get_user(uname: 'str') -> 'SQL record':
    with UseDatabase(dbconfig) as cursor:
        _SQL = """select * from user_details where username=%s limit 1"""
        cursor.execute(_SQL, (uname,))
        return cursor.fetchone()
