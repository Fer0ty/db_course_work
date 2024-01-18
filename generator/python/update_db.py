import psycopg2
from main import tables

table_names = [i.name for i in tables]

if __name__ == "__main__":
    conn = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="postgres",
        port=5432
    )
    # with conn.cursor() as curs:
    #     curs.execute(open(f"../sql/triggers.sql", "r").read())
    # conn.commit()

    for name in table_names:
        with conn.cursor() as curs:
            print(f"Current table: {name}")
            curs.execute(f"DROP TABLE IF EXISTS {name} CASCADE;")
            curs.execute(open(f"../sql/{name}.schema.sql", "r").read())
            curs.execute(open(f"../sql/{name}.data.sql", "r").read())
            conn.commit()



