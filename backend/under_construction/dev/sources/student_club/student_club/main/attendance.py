# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import student_club # noqa F401 


@source(resource=student_club)
class Attendance:
    _table = "attendance"
    _unique_name = "student_club.student_club.main.Attendance"
    _schema = "main"
    _database = "student_club"
    _twin_path = "data/student_club/main/student_club.duckdb"
    _path = "data/dev_databases/student_club/student_club.sqlite"
    _row_count = 326
    _col_replace = {}

    link_to_event: t.String(nullable=True) = Field(description='''The unique identifier of the event which was attended. Additional context: References the Event table''', foreign_key=('Event', 'event_id'))
    link_to_member: t.String(nullable=True) = Field(description='''The unique identifier of the member who attended the event. Additional context: References the Member table''', foreign_key=('Member', 'member_id'))

