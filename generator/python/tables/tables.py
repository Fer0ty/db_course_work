from generator.python.tables.base import *
from faker import Faker

fake = Faker()


class AccountTable(Table):
    ACCOUNT_ID = Field("account_id", SERIAL, [PK])
    PASSWORD = Field("password", TEXT, [NOT_NULL], generate_callback=fake.password)
    EMAIL = Field("email", TEXT, generate_callback=fake.email)
    PHONE_NUMBER = Field("phone_number", TEXT, generate_callback=fake.phone_number)
    CITY = Field("city", TEXT, generate_callback=fake.city)

    def __init__(self):
        super().__init__("accounts",
                         [
                             self.ACCOUNT_ID,
                             self.PASSWORD,
                             self.EMAIL,
                             self.PHONE_NUMBER,
                             self.CITY
                         ])


ACCOUNT_TABLE = AccountTable()


class ProblemTable(Table):
    PROBLEM_ID = Field("problem_id", SERIAL, [PK], generate_callback=None)
    PROBLEM_TEXT = Field("problem_text", TEXT, [NOT_NULL], generate_callback=None)
    ANSWER = Field("answer", TEXT, [NOT_NULL], generate_callback=None)

    def __init__(self):
        super().__init__("problems",
                         [
                             self.PROBLEM_ID,
                             self.PROBLEM_TEXT,
                             self.ANSWER
                         ])


PROBLEM_TABLE = ProblemTable()


class RoleTable(Table):
    ID = Field("id", SERIAL, [PK])
    NAME = Field("name", TEXT, [NOT_NULL, UNIQUE],
                 generate_callback=role_table_name_callback)

    def __init__(self):
        super().__init__("roles",
                         [
                             self.ID,
                             self.NAME
                         ])


ROLE_TABLE = RoleTable()


class UserTable(Table):
    LOGIN = Field("login", TEXT, [PK],
                  generate_callback=lambda: fake.first_name()[:4].lower() + fake.last_name()[:4].lower())
    ACCOUNT_ID = Field("account_id", INT, [UNIQUE, NOT_NULL],
                       reference=Reference(ACCOUNT_TABLE, AccountTable.ACCOUNT_ID, ReferenceType.ONE_TO_ONE))
    NAME = Field("name", TEXT, [NOT_NULL], generate_callback=fake.first_name)
    SURNAME = Field("surname", TEXT, [NOT_NULL], generate_callback=fake.last_name)
    FAMILY_NAME = Field("last_name", TEXT, generate_callback=lambda: fake.first_name() + "ich")
    BIRTHDATE = Field("birthdate", DATE, [NOT_NULL], generate_callback=fake.date)
    ROLE_ID = Field("role_id", INT, [NOT_NULL],
                    reference=Reference(ROLE_TABLE, RoleTable.ID, ReferenceType.MANY_TO_ONE))

    def __init__(self):
        super().__init__("users",
                         [
                             self.LOGIN,
                             self.ACCOUNT_ID,
                             self.NAME,
                             self.SURNAME,
                             self.FAMILY_NAME,
                             self.BIRTHDATE,
                             self.ROLE_ID
                         ])


USER_TABLE = UserTable()
