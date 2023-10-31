from datetime import datetime, timedelta

from pymysql import connect, Connection

from structure import Currency
from util import get_secret


last_connect = None
database = None
refresh_rate = timedelta(hours=1)
def get_database() -> Connection:
    global database, last_connect

    # if cached, return
    now = datetime.now()
    if database is not None and last_connect is not None \
            and now - refresh_rate <= last_connect:
        return database

    # close connection and reconnect database
    if database is not None:
        database.close()

    database = connect(
        host=get_secret('database.host'),
        user=get_secret('database.user'),
        password=get_secret('database.password'),
        database=get_secret('database.database'),
    )
    last_connect = now

    return database


def get_currencies() -> list[Currency]:
    result = list()

    with get_database().cursor() as cursor:
        cursor.execute('SELECT * FROM currency')

        for row in cursor.fetchall():
            currency = Currency.from_row(row)
            result.append(currency)

    return result


def get_currency(code: str) -> Currency:
    with get_database().cursor() as cursor:
        cursor.execute('SELECT * FROM currency WHERE code = %s', (code,))
        return Currency.from_row(cursor.fetchone())


def set_currency(currency: Currency):
    database = get_database()
    with database.cursor() as cursor:
        cursor.execute('UPDATE currency SET frozen = %s WHERE code = %s',
                       (currency.frozen, currency.code))
        database.commit()

