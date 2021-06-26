
from contextlib import contextmanager
from psycopg2.pool import ThreadedConnectionPool
# dbname="postgres", user="postgres", password="passwords with spaces", host="localhost", port ="5432"
# dsn = "host=localhost port=5432 dbname=STUDENT2 user=root password=1234"
# db_pool = ThreadedConnectionPool(minconn=2, maxconn=10, dsn=dsn)
db_pool = ThreadedConnectionPool(2, 10,
                              database="student2",
                              user="root",
                              password="1234",
                              host="localhost",
                              port="5432")

@contextmanager
def db_block():
    conn = db_pool.getconn()
    try:
        with conn.cursor() as cur:
            yield cur
            conn.commit()
    except:
        conn.rollback()
        raise
    finally:
        db_pool.putconn(conn)
