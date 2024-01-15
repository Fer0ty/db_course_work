import random
import re
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

# pipyao))
company = ['YANDEX', 'TINKOFF', 'MTS', 'OZON', 'WILDBERRIES', 'LIPTSOFT', 'AMAZON', 'GOOGLE', 'MICROSOFT', 'APPLE',
           'BEELINE', 'MEGAFON']
season = ["WINTER", 'SPRING', 'SUMMER', 'FALL']
year = ['2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022',
        '2023']


def generate_date():
    start = fake.date()
    y, m, d = start.split('-')
    m = int(m) + 1
    if m < 10:
        m = '0' + str(m)
    end = y + '-' + str(m) + '-' + d
    return start, end


class ContestTable(Table):
    start, end = generate_date()
    CONTEST_ID = Field("contest_id", SERIAL, [PK])
    NAME = Field('name', TEXT, [NOT_NULL],
                 generate_callback=lambda: random.choice(company) + '_' + random.choice(season) + '_' + random.choice(
                     year))

    START_DATE = Field("start_date", DATE, [NOT_NULL], generate_callback=lambda: generate_date()[0])
    END_DATE = Field("end_date", DATE, [NOT_NULL], generate_callback=lambda: generate_date()[1])
    CREATOR = Field("creator", INT, [NOT_NULL], reference=Reference(USER_TABLE, UserTable.ACCOUNT_ID,
                                                                    ReferenceType.MANY_TO_ONE))

    def __init__(self):
        super().__init__("contest",
                         [self.CONTEST_ID,
                          self.NAME,
                          self.START_DATE,
                          self.END_DATE,
                          self.CREATOR])


CONTEST_TABLE = ContestTable()


class ProblemSolution(Table):
    LOGIN = Field("login", TEXT, [NOT_NULL],
                  reference=Reference(USER_TABLE, USER_TABLE.LOGIN, ReferenceType.MANY_TO_ONE))
    CONTEST_ID = Field("contest_id", INT, [NOT_NULL],
                       reference=Reference(CONTEST_TABLE, CONTEST_TABLE.CONTEST_ID, ReferenceType.MANY_TO_ONE))
    PROBLEM_ID = Field("problem_id", INT, [NOT_NULL],
                       reference=Reference(PROBLEM_TABLE, PROBLEM_TABLE.PROBLEM_ID, ReferenceType.MANY_TO_ONE))
    USER_ANSWER = Field("user_answer", TEXT, generate_callback=fake.text)
    STATUS = Field('status', BOOLEAN, generate_callback=lambda: random.randint(0,1))

    # todo Добавить составной PK

    def __init__(self):
        super().__init__("problem_solution",
                         [self.LOGIN,
                          self.CONTEST_ID,
                          self.PROBLEM_ID,
                          self.USER_ANSWER,
                          self.STATUS])


PROBLEM_SOLUTION_TABLE = ProblemSolution()


def generate_devname():
    a = fake.text()
    a = a.split(' ')[0] + '_' + a.split(' ')[1]
    return a


class DevTeam(Table):
    DEVTEAM_ID = Field("devteam_id", SERIAL, [PK])
    NAME = Field("name", TEXT, [NOT_NULL], generate_callback=generate_devname())

    def __init__(self):
        super().__init__("devteam",
                         [self.DEVTEAM_ID,
                          self.NAME])


DEVTEAM = DevTeam()


class Developer(Table):
    LOGIN = Field("login", TEXT, [NOT_NULL],
                  reference=Reference(USER_TABLE, UserTable.LOGIN, ReferenceType.MANY_TO_ONE))
    DEVTEAM_ID = Field("devteam", INT, [NOT_NULL],
                       reference=Reference(DEVTEAM, DevTeam.DEVTEAM_ID, ReferenceType.MANY_TO_ONE))

    # todo Добавить составной PK
    def __init__(self):
        super().__init__("developer",
                         [self.LOGIN,
                          self.DEVTEAM_ID])


DEVELOPER = Developer()


class TechInterview(Table):
    TECHINTERVIW_ID = Field('techinterview_id', SERIAL, [PK])
    LOGIN = Field('login', TEXT, [NOT_NULL],
                  reference=Reference(USER_TABLE, UserTable.LOGIN, ReferenceType.MANY_TO_ONE))
    # todo check timestamp, status
    DATE = Field('date', TIMESTAMP, [NOT_NULL], generate_callback=fake.date_time)
    STATUS = Field('status', BOOLEAN, generate_callback=lambda: random.randint(0,1))
    INTERVIEWER_LOGIN = Field('interviwer_id', INT, [NOT_NULL],
                              reference=Reference(USER_TABLE, UserTable.LOGIN, ReferenceType.MANY_TO_ONE))

    def __init__(self):
        super().__init__('techinterview',
                         [self.TECHINTERVIW_ID,
                          self.LOGIN,
                          self.DATE,
                          self.STATUS,
                          self.INTERVIEWER_LOGIN])


TECHINTERVIEW = TechInterview()


class TeamInterview(Table):
    TEAMINTERVIEW_ID = Field('teaminterview_id', SERIAL, [PK])
    LOGIN = Field('login', TEXT, [NOT_NULL],
                  reference=Reference(USER_TABLE, UserTable.LOGIN, ReferenceType.MANY_TO_ONE))
    TECHINTERVIEW_ID = Field('techinterview_id', INT, [NOT_NULL],
                             reference=Reference(TECHINTERVIEW, TechInterview.TECHINTERVIW_ID,
                                                 ReferenceType.MANY_TO_ONE))
    DATE = Field('date', TIMESTAMP, [NOT_NULL], generate_callback=fake.date_time)
    STATUS = Field('status', BOOLEAN)
    DEVTEAM_ID = Field('devteam_id', INT, [NOT_NULL],
                       reference=Reference(DEVTEAM, DevTeam.DEVTEAM_ID, ReferenceType.MANY_TO_ONE))
    COMMENT = Field('comment', TEXT, generate_callback=fake.text)

    def __init__(self):
        super().__init__('teaminterview',
                         [self.TEAMINTERVIEW_ID,
                          self.LOGIN,
                          self.TECHINTERVIEW_ID,
                          self.DATE,
                          self.STATUS,
                          self.DEVTEAM_ID,
                          self.COMMENT])


TEAMINTERVIEW = TeamInterview()


class ProblemFeedback(Table):
    TECHINTERVIEW_ID = Field('techinterview_id', INT, [NOT_NULL],
                             reference=Reference(TECHINTERVIEW, TechInterview.TECHINTERVIW_ID,
                                                 ReferenceType.MANY_TO_ONE))
    COMMENT = Field('comment', TEXT, generate_callback=fake.text)
    PROBLEM_ID = Field("problem_id", INT, [NOT_NULL],
                       reference=Reference(PROBLEM_TABLE, PROBLEM_TABLE.PROBLEM_ID, ReferenceType.MANY_TO_ONE))

    def __init__(self):
        super().__init__('problem_feedback',
                         [self.TECHINTERVIEW_ID,
                          self.COMMENT,
                          self.PROBLEM_ID])


PROBLEM_FEEDBACK = ProblemFeedback()


class Offer(Table):
    OFFER_ID = Field('offer_id', SERIAL, [PK])
    LOGIN = Field('login', TEXT, [NOT_NULL],
                  reference=Reference(USER_TABLE, UserTable.LOGIN, ReferenceType.MANY_TO_ONE))
    DEVTEAM_ID = Field('devteam_id', INT, [NOT_NULL],
                       reference=Reference(DEVTEAM, DevTeam.DEVTEAM_ID, ReferenceType.MANY_TO_ONE))
    SALARY = Field('salary', INT, [NOT_NULL], generate_callback=lambda: random.randint(85, 450) * 1000)
    START_DATE = Field('start_date', DATE, [NOT_NULL], generate_callback=lambda: generate_date()[0])
    END_DATE = Field('end_date', DATE, [NOT_NULL], generate_callback=lambda: generate_date()[1])
    STATUS = Field('status', BOOLEAN)

    # todo unique

    def __init__(self):
        super().__init__('offer',
                         [self.OFFER_ID,
                          self.LOGIN,
                          self.DEVTEAM_ID,
                          self.SALARY,
                          self.START_DATE,
                          self.END_DATE,
                          self.STATUS])


OFFER = Offer()
