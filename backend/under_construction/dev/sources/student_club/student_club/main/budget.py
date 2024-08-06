# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import student_club # noqa F401 


@source(resource=student_club)
class Budget:
    _table = "budget"
    _unique_name = "student_club.student_club.main.Budget"
    _schema = "main"
    _database = "student_club"
    _twin_path = "data/student_club/main/student_club.duckdb"
    _path = "data/dev_databases/student_club/student_club.sqlite"
    _row_count = 52
    _col_replace = {}

    budget_id: t.String(nullable=True) = Field(description='''A unique identifier for the budget entry''', primary_key=True)
    category: t.String(nullable=True) = Field(description='''The area for which the amount is budgeted, such as, advertisement, food, parking''')
    spent: t.Float64(nullable=True) = Field(description='''The total amount spent in the budgeted category for an event.. Additional context: the unit is dollar. This is summarized from the Expense table''')
    remaining: t.Float64(nullable=True) = Field(description='''A value calculated as the amount budgeted minus the amount spent. Additional context: the unit is dollar 
 If the remaining < 0, it means that the cost has exceeded the budget.''')
    amount: t.Int64(nullable=True) = Field(description='''The amount budgeted for the specified category and event. Additional context: the unit is dollar 

some computation like: amount = spent + remaining ''')
    event_status: t.String(nullable=True) = Field(description='''the status of the event. Additional context: Closed / Open/ Planning 
 
• Closed: It means that the event is closed. The spent and the remaining won't change anymore.
• Open: It means that the event is already opened. The spent and the remaining will change with new expenses.
• Planning: The event is not started yet but is planning. The spent and the remaining won't change at this stage. ''')
    link_to_event: t.String(nullable=True) = Field(description='''The unique identifier of the event to which the budget line applies.. Additional context: References the Event table''', foreign_key=('Event', 'event_id'))

