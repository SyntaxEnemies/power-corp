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


def get_column_names(table: str) -> list:
    with UseDatabase(dbconfig) as cursor:
        _SQL = """describe {}""".format(table)
        cursor.execute(_SQL)
        schema = cursor.fetchall()

    columns = []
    for row in schema:
        columns.append(row[0])
    return columns


def get_user(uname: str) -> dict:
    keys = get_column_names('user_details')

    with UseDatabase(dbconfig) as cursor:
        _SQL = """select * from user_details where username=%s limit 1"""
        cursor.execute(_SQL, (uname,))
        values = cursor.fetchone()

    return dict(zip(keys, values))


def add_user(userdata: dict) -> None:
    with UseDatabase(dbconfig) as cursor:
        _SQL = dict_to_sql(userdata, 'user_details')
        cursor.execute(_SQL, tuple(userdata.values()))
