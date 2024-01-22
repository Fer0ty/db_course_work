import psycopg2
from main import tables

table_names = [i.name for i in tables]
triggers_by_table_name = {
    "offer": ["""CREATE TRIGGER check_user_offer_limit_trigger
BEFORE INSERT ON offer
FOR EACH ROW
EXECUTE FUNCTION check_user_offer_limit();""",
              """CREATE TRIGGER check_offer_salary_trigger
BEFORE INSERT OR UPDATE ON offer
FOR EACH ROW
EXECUTE FUNCTION check_salary();""",
              """CREATE TRIGGER check_offerdate_trigger
BEFORE INSERT OR UPDATE ON offer
FOR EACH ROW
EXECUTE FUNCTION check_dates();"""],
    "contest": ["""CREATE TRIGGER check_contestdate_trigger
BEFORE INSERT OR UPDATE ON contest
FOR EACH ROW
EXECUTE FUNCTION check_dates();
"""],
    "accounts": ["""CREATE TRIGGER check_password_length_trigger
BEFORE INSERT OR UPDATE ON accounts
FOR EACH ROW
EXECUTE FUNCTION check_password_length();"""],
    "techinterview": ["""CREATE TRIGGER check_user_interview_limit_trigger
BEFORE INSERT ON techinterview
FOR EACH ROW
EXECUTE FUNCTION check_user_interview_limit();"""]
}

if __name__ == "__main__":
    conn = psycopg2.connect(
        host="postgresql://pg",
        database="studs",
        user="s334645",
        password="eNiIXg15sQmP6nDf",
        port="5432"
    )
    with conn.cursor() as curs:
        curs.execute(open(f"../sql/triggers.sql", "r").read())
    conn.commit()

    for name in table_names:
        with conn.cursor() as curs:
            print(f"Current table: {name}")
            curs.execute(f"DROP TABLE IF EXISTS {name} CASCADE;")
            curs.execute(open(f"../sql/{name}.schema.sql", "r").read())

            triggers = triggers_by_table_name.get(name, None)
            if triggers:
                for trig in triggers:
                    curs.execute(trig)
                conn.commit()

            curs.execute(open(f"../sql/{name}.data.sql", "r").read())
            conn.commit()
