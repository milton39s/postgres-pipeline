from urllib.parse import urlparse
import psycopg2

class PostgresTransfer:
    
    def __init__(self, src_conn_uri, dst_conn_uri, dst_table_name, src_table_name, primary_keys, indexes, src_sql):
        self.src_conn_uri = src_conn_uri
        self.dst_conn_uri = dst_conn_uri
        self.dst_table_name = dst_table_name
        self.src_table_name = src_table_name
        self.primary_keys = primary_keys
        self.indexes = indexes
        self.src_sql = src_sql
    
    def execute(self):
        dst = urlparse(self.dst_conn_uri)
        src = urlparse(self.src_conn_uri)
        conn_dts = psycopg2.connect(database=dst.path[1:], user=dst.username, password=dst.password, host=dst.hostname, port=dst.port)
        conn_src = psycopg2.connect(database=src.path[1:], user=src.username, password=src.password, host=src.hostname, port=src.port)
        cur_dst = conn_dts.cursor()
        cur_src = conn_src.cursor()
        try:
            cur_dst.execute(f"create table if not exists {self.dst_table_name}_backup as (select * from {self.dst_table_name});")
            cur_dst.execute(f"truncate table {self.dst_table_name};")
            print("try1")
        except:
            cur_dst.execute("rollback")
            cur_dst.execute(f"""
                create table if not exists {self.dst_table_name} (
                    bid bigint,
                    fid bigint,
                    price double precision,
                    primary key ({','.join(self.primary_keys)}));
                create unique index idx on {self.dst_table_name}({','.join(self.indexes)});
                """)
            print("Table didn't exist in anal_db")
        try:
            cur_src.execute(self.src_sql)
            data_src = cur_src.fetchall()
            print(data_src)
            records_template = ','.join(['%s'] * len(data_src))
            cur_dst.execute(f"insert into {self.dst_table_name} values {records_template};", data_src)
            cur_dst.execute(f"drop table if exists {self.dst_table_name}_backup;")
            print("try2")
        except:
            cur_dst.execute("rollback")
            cur_dst.execute(f"drop table if exists {self.dst_table_name};")
            cur_dst.execute(f"alter table if exists {self.dst_table_name}_backup rename to {self.dst_table_name};")
            print("Data insert failed")
        

###### test

t = PostgresTransfer(
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

t.execute()