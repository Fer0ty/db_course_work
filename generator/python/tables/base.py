import random
from typing import Tuple, List, Callable, Dict, TypeVar, Type, Set
from enum import Enum

# region constants
PK = "PRIMARY KEY"
UNIQUE = "UNIQUE"
NOT_NULL = "NOT NULL"
TEXT = "TEXT"
SERIAL = "SERIAL"
INT = "INT"
DATE = "DATE"
BOOLEAN = "BOOLEAN"
TIMESTAMP = "TIMESTAMP"
T = TypeVar("T")
E = TypeVar("E", bound=Enum)
ROLE_TABLE_NAME_CNT = 0


class ReferenceType(Enum):
    ONE_TO_ONE = 1,
    MANY_TO_ONE = 2


class RoleEnum(Enum):
    COMPANY = 1,
    HR = 2,
    DEVELOPER = 3,
    USER = 4

# endregion


class Field:

    def __init__(self, name: str, value_type: str):
        self.name = name
        self.value_type = value_type


class Table:

    def __init__(self, name: str):
        self.name = name


class RecordValue:

    def __init__(self, name: str, value: str):
        self.name = name
        self.value = value


class Reference:

    def __init__(self, table: Table, field: Field, reference_type: ReferenceType):
        self.table = table
        self.field = field
        self.reference_type = reference_type


class Record:

    def __init__(self, table_name: str, data: List[RecordValue]):
        self.table_name = table_name
        self.data = data
        self.data_dict: Dict[str, str] = {i.name: i.value for i in data}

    def generate_sql(self) -> str:
        return "INSERT INTO {} ({})\nVALUES ({});\n\n"\
            .format(self.table_name, ",".join(i.name for i in self.data), ",".join(i.value for i in self.data))

    def get_field_value_by_name(self, field_name: str):
        value = self.data_dict.get(field_name, None)
        if not value:
            raise Exception(f"no field {field_name} in table {self.table_name}")
        return value


class Field:

    def __init__(self, name: str, value_type: str, constraints: List[str] = None,
                 reference: Reference = None, generate_callback: Callable[[], str] = None):
        self.name = name
        self.value_type = value_type
        self.constraints = constraints
        self.reference = reference
        self.generate_callback = generate_callback

    def generate_value(self, table: Table) -> str:
        if self.value_type == SERIAL:
            return str(get_sequence_value(self))

        if self.reference is None and self.generate_callback is None:
            raise Exception(f"no reference and callback in field {self.name} and field is not SERIAL")

        if self.reference is None:
            value = str(self.generate_callback())
            if self.value_type in [TEXT, DATE, BOOLEAN, TIMESTAMP]:
                value = f"'{value}'"
        else:
            values = data.get(self.reference.table, None)
            if not values:
                raise Exception(f"no data for table {self.reference.table.name}")
            # Serial are compatible with int and long, so its hard to just compare them
            if self.value_type != self.reference.field.value_type and self.reference.field.value_type != SERIAL:
                raise Exception(f"Type mismatch in fk for table {table.name}, field {self.name}")

            if self.reference.reference_type == ReferenceType.MANY_TO_ONE:
                value = get_random_list_element(values).get_field_value_by_name(self.reference.field.name)
            elif self.reference.reference_type == ReferenceType.ONE_TO_ONE:
                idx = get_one_to_one_counter(self.reference.field, self)
                if idx >= len(values):
                    raise Exception(f"Not enough values in table {self.reference.table} for one to one dependency:"
                                    f" field {self.name} table {table}")
                value = values[idx].get_field_value_by_name(self.name)
            else:
                raise Exception(f"reference type {self.reference.reference_type} not implemented")

        if self.constraints and (UNIQUE in self.constraints or PK in self.constraints):
            if value in unique_dict[self]:
                return ""
            unique_dict[self].add(value)

        return generate_nullable(value) if self.is_nullable() else value

    def is_nullable(self):
        return not self.constraints or (NOT_NULL not in self.constraints and PK not in self.constraints)

    def generate_sql(self) -> str:
        sql = f"\t{self.name} {self.value_type}"
        if self.constraints:
            sql += " " + " ".join(self.constraints)
            if self.reference:
                sql += f" REFERENCES {self.reference.table.name}({self.reference.field.name})"
        return sql


def get_field_value_by_name(name: str, fields: List[RecordValue]):
    for i in fields:
        if i.name == name:
            return i.value
    return None


class Table:

    def __init__(self, name: str, fields: List[Field], constraints: List[Tuple[str, List[Field]]] = None):
        self.name = name
        self.fields = fields
        self.constraints = constraints

    def generate_record(self) -> Record:
        fields = [RecordValue(i.name, i.generate_value(self)) for i in self.fields]

        # Now it means that unique constraint was broken and we can't generate new value
        if any(i.value == "" for i in fields):
            return None
        if self.constraints:
            for const in self.constraints:
                cur_hash = list_hash(const[1])
                if const[0] not in [PK, UNIQUE]:
                    continue
                cur_values = "$#".join([get_field_value_by_name(i.name, fields) for i in const[1]])
                if cur_values in unique_table_dict[cur_hash]:
                    return None
                unique_table_dict[cur_hash].add(cur_values)
        return Record(self.name, fields)

    def generate_create_sql(self):
        fields_sql = ",\n".join(i.generate_sql() for i in self.fields)
        sql = f"CREATE TABLE IF NOT EXISTS {self.name} (\n{fields_sql}"
        if self.constraints:
            constraints_sql = ",\n".join("""\t{}({})""".format(i[0], ", ".join(f.name for f in i[1]))
                                     for i in self.constraints) if self.constraints else ""
            sql += ",\n" + constraints_sql
        sql += "\n);"
        return sql


def get_random_list_element(l: List[T]) -> T:
    return l[random.randint(0, len(l) - 1)]


def generate_nullable(value: T) -> T:
    if random.random() < 0.1:
        return "null"
    return value


def get_all_enum_values(en: Type[E]) -> List[E]:
    return [e for e in en]


def get_sequence_value(key: Field) -> int:
    value = sequences[key]
    sequences[key] += 1
    return value


def get_one_to_one_counter(original_field: Field, foreign_key: Field) -> int:
    value = one_to_one_counter[(original_field, foreign_key)]
    one_to_one_counter[(original_field, foreign_key)] += 1
    return value


def role_table_name_callback() -> str:
    global ROLE_TABLE_NAME_CNT
    ROLE_TABLE_NAME_CNT += 1
    values = get_all_enum_values(RoleEnum)
    if ROLE_TABLE_NAME_CNT > len(values):
        return values[0].name
    return get_all_enum_values(RoleEnum)[ROLE_TABLE_NAME_CNT - 1].name


def list_hash(l: List[T]) -> int:
    base = 37
    cur_hash = 0
    for i in l:
        cur_hash = cur_hash * base + hash(i)
    return cur_hash


data: Dict[Table, List[Record]] = {}
sequences: Dict[Field, int] = {}
one_to_one_counter: Dict[Tuple[Field, Field], int] = {}
unique_dict: Dict[Field, Set[str]] = {}
unique_table_dict: Dict[int, Set[str]] = {}
