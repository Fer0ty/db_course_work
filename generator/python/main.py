import os.path

from tables.tables import *
from tables.base import Table

tables: List[Table] = [ROLE_TABLE, ACCOUNT_TABLE, USER_TABLE, PROBLEM_TABLE]


def write_create_sql(table: Table) -> None:
    with open(f"generator/sql/{table.name}.schema.sql", "w") as f:
        f.write(table.generate_create_sql())


def write_all_create_sql() -> None:
    [write_create_sql(table) for table in tables]


def generate_data_sql(table: Table, cnt: int) -> None:
    cur_list = data.get(table, [])
    if len(cur_list) == 0:
        data[table] = cur_list

    with open(f"generator/sql/{table.name}.data.sql", "w") as f:
        records_cnt = 0
        for i in range(cnt):
            record = table.generate_record()
            if record is None:
                continue
            cur_list.append(record)
            f.write(record.generate_sql())
            records_cnt += 1
            if records_cnt % (cnt // 10) == 0:
                print(f"[debug] Generated {records_cnt} elements for table {table.name}")
        print(f"Total number of rows generated for table {table.name} is {records_cnt}")


def generate_all_data_sql(cnt: int, exclude_table: List[Table] = None) -> None:
    for table in tables:
        initialize_one_to_one_counter(table)
        initialize_uniques(table)
        if table not in exclude_table:
            generate_data_sql(table, cnt)


def initialize_sequences() -> None:
    for table in tables:
        for field in table.fields:
            if SERIAL == field.value_type:
                sequences[field] = 1


def initialize_one_to_one_counter(table: Table) -> None:
    for field in table.fields:
        if field.reference and field.reference.reference_type == ReferenceType.ONE_TO_ONE:
            one_to_one_counter[(field.reference.field, field)] = 0


def initialize_uniques(table: Table) -> None:
    for field in table.fields:
        if field.constraints and UNIQUE in field.constraints:
            unique_dict[field] = set()


def create_sql_dir_if_not_exists() -> None:
    path = "generator/sql"
    if not os.path.exists(path):
        os.mkdir(path)


if __name__ == "__main__":
    create_sql_dir_if_not_exists()
    write_all_create_sql()

    initialize_sequences()
    generate_all_data_sql(10000, exclude_table=[PROBLEM_TABLE])
