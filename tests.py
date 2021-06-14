from urllib.parse import urlparse

import psycopg2
import pytest

from .solution import PostgresTransfer


def get_conn(uri):
    result = urlparse(uri)
    username = result.username
    password = result.password
    database = result.path[1:]
    hostname = result.hostname
    port = result.port
    connection = psycopg2.connect(
        database=database, user=username, password=password, host=hostname, port=port
    )
    return connection


ANAL_DB_URI = "postgres://postgres:@localhost:54321/anal_db"
APP_DB_URI = "postgres://postgres:@localhost:54320/app_db"


def run(uri, sql, return_values=False):
    with get_conn(uri) as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            if return_values:
                return cur.fetchall()


@pytest.fixture
def transfer():
    return PostgresTransfer(
        src_conn_uri="postgres://postgres:@localhost:54320/app_db",
        dst_conn_uri="postgres://postgres:@localhost:54321/anal_db",
        dst_table_name="public.app_db_flights",
        src_table_name="public.flights",
        primary_keys=["bid", "fid"],
        indexes=["bid"],
        src_sql="""
                select bid, fid, price
                from flights
            """
    )


def test_transfer_simple(transfer):

    # create inital data
    run(ANAL_DB_URI, "drop table if exists public.app_db_flights;")
    run(APP_DB_URI, "truncate table public.flights;")
    run(APP_DB_URI, """
        insert into flights(bid, fid, price) values(1, 1, 1.0);
        insert into flights(bid, fid, price) values(2, 2, 2.0);
        insert into flights(bid, fid, price) values(3, 3, 3.0);
        insert into flights(bid, fid, price) values(4, 4, 4.0);
    """)

    # check if data are copied correctly
    transfer.execute()
    data = run(
        ANAL_DB_URI,
        "select bid, fid, price from app_db_flights order by bid;",
        return_values=True,
    )

    assert data == [(1, 1, 1.0), (2, 2, 2.0), (3, 3, 3.0), (4, 4, 4.0)]

    # change data
    # check if changes are propagated correctly
    run(APP_DB_URI, "update flights set price = 2.5 where bid = 2;")
    transfer.execute()
    data = run(
        ANAL_DB_URI,
        "select bid, fid, price from app_db_flights order by bid;",
        return_values=True,
    )
    assert data == [(1, 1, 1.0), (2, 2, 2.5), (3, 3, 3.0), (4, 4, 4.0)]
