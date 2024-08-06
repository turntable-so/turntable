# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import student_club # noqa F401 


@source(resource=student_club)
class Expense:
    _table = "expense"
    _unique_name = "student_club.student_club.main.Expense"
    _schema = "main"
    _database = "student_club"
    _twin_path = "data/student_club/main/student_club.duckdb"
    _path = "data/dev_databases/student_club/student_club.sqlite"
    _row_count = 32
    _col_replace = {}

    expense_id: t.String(nullable=True) = Field(description='''unique id of income''', primary_key=True)
    expense_description: t.String(nullable=True) = Field(description='''A textual description of what the money was spend for''')
    expense_date: t.String(nullable=True) = Field(description='''The date the expense was incurred. Additional context: e.g. YYYY-MM-DD''')
    cost: t.Float64(nullable=True) = Field(description='''The dollar amount of the expense. Additional context: the unit is dollar''')
    approved: t.String(nullable=True) = Field(description='''A true or false value indicating if the expense was approved. Additional context: true/ false''')
    link_to_member: t.String(nullable=True) = Field(description='''The member who incurred the expense''', foreign_key=('Member', 'member_id'))
    link_to_budget: t.String(nullable=True) = Field(description='''The unique identifier of the record in the Budget table that indicates the expected total expenditure for a given category and event. . Additional context: References the Budget table''', foreign_key=('Budget', 'budget_id'))

