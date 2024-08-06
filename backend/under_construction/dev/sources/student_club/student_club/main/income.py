# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import student_club # noqa F401 


@source(resource=student_club)
class Income:
    _table = "income"
    _unique_name = "student_club.student_club.main.Income"
    _schema = "main"
    _database = "student_club"
    _twin_path = "data/student_club/main/student_club.duckdb"
    _path = "data/dev_databases/student_club/student_club.sqlite"
    _row_count = 36
    _col_replace = {}

    income_id: t.String(nullable=True) = Field(description='''A unique identifier for each record of income''', primary_key=True)
    date_received: t.String(nullable=True) = Field(description='''the date that the fund received''')
    amount: t.Int64(nullable=True) = Field(description='''amount of funds. Additional context: the unit is dollar''')
    source: t.String(nullable=True) = Field(description='''A value indicating where the funds come from such as dues, or the annual university allocation''')
    notes: t.String(nullable=True) = Field(description='''A free-text value giving any needed details about the receipt of funds''')
    link_to_member: t.String(nullable=True) = Field(description='''link to member''', foreign_key=('Member', 'member_id'))

