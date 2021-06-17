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

    def run(self, conne, sql, return_values=False):
        with conne as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                if return_values:
                    return cur.fetchall()
    
    def execute(self):
        dst = urlparse(self.dst_conn_uri)
        src = urlparse(self.src_conn_uri)
        conn_dts = psycopg2.connect(database=dst.path[1:], user=dst.username, password=dst.password, host=dst.hostname, port=dst.port)
        conn_src = psycopg2.connect(database=src.path[1:], user=src.username, password=src.password, host=src.hostname, port=src.port)

        # If the data in "flights" (source) has not changed, end the execution. 
        # In this way, resources will be saved if the process runs frequently.
        try:
            data_src = self.run(conn_src, self.src_sql, True)
            data_dts = self.run(conn_dts, f"select bid, fid, price from {self.dst_table_name}", True)
            if data_dts == data_src:
                return
        except:
            pass

        try:
            # create a backup in case the insert fails, the data will be restored
            self.run(conn_dts, f"create table if not exists {self.dst_table_name}_backup as (select * from {self.dst_table_name});")
            self.run(conn_dts, f"truncate table {self.dst_table_name};")
        except:
            self.run(conn_dts, "rollback")
            self.run(conn_dts, f"""
                create table if not exists {self.dst_table_name} (
                    bid bigint,
                    fid bigint,
                    price double precision,
                    primary key ({','.join(self.primary_keys)}));
                create unique index idx on {self.dst_table_name}({','.join(self.indexes)});
                """)

        try:
            data_src = self.run(conn_src, self.src_sql, True)
            records_template = str(data_src).strip('[]')
            self.run(conn_dts, f"insert into {self.dst_table_name}(bid, fid, price) values {records_template};")
            self.run(conn_dts, f"drop table if exists {self.dst_table_name}_backup;")
        except:
            self.run(conn_dts, "rollback")
            self.run(conn_dts, f"drop table if exists {self.dst_table_name};")
            self.run(conn_dts, f"alter table if exists {self.dst_table_name}_backup rename to {self.dst_table_name[7:]};")