# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import student_club # noqa F401 


@source(resource=student_club)
class Event:
    _table = "event"
    _unique_name = "student_club.student_club.main.Event"
    _schema = "main"
    _database = "student_club"
    _twin_path = "data/student_club/main/student_club.duckdb"
    _path = "data/dev_databases/student_club/student_club.sqlite"
    _row_count = 42
    _col_replace = {}

    event_id: t.String(nullable=True) = Field(description='''A unique identifier for the event''', primary_key=True)
    event_name: t.String(nullable=True) = Field(description='''event name''')
    event_date: t.String(nullable=True) = Field(description='''The date the event took place or is scheduled to take place. Additional context: e.g. 2020-03-10T12:00:00''')
    type: t.String(nullable=True) = Field(description='''The kind of event, such as game, social, election''')
    notes: t.String(nullable=True) = Field(description='''A free text field for any notes about the event''')
    location: t.String(nullable=True) = Field(description='''Address where the event was held or is to be held or the name of such a location''')
    status: t.String(nullable=True) = Field(description='''One of three values indicating if the event is in planning, is opened, or is closed. Additional context: Open/ Closed/ Planning''')

