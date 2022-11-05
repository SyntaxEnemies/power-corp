from DBcm import UseDatabase
from main import app

# Load database configuration into dbconfig dict
dbconfig = {k.removeprefix('DB_').lower(): v for k, v in app.config.items() if k.startswith('DB_')}


def dict_to_sql(insert_data: dict, table: str) -> str:
    placeholders = ', '.join(['%s'] * len(insert_data))
    columns = ', '.join(insert_data.keys())

    template = 'insert into {0} ({1}) values ({2})'
    sql = template.format(table,columns, placeholders)
    return sql


def get_user(uname: str) -> list[tuple]:
    with UseDatabase(dbconfig) as cursor:
        _SQL = """select * from user_details where username=%s limit 1"""
        cursor.execute(_SQL, (uname,))
        return cursor.fetchone()


def add_user(userdata: dict) -> None:
    with UseDatabase(dbconfig) as cursor:
        _SQL = dict_to_sql(userdata, 'user_details')
        cursor.execute(_SQL, tuple(userdata.values()))
