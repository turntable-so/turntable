# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import student_club # noqa F401 


@source(resource=student_club)
class Major:
    _table = "major"
    _unique_name = "student_club.student_club.main.Major"
    _schema = "main"
    _database = "student_club"
    _twin_path = "data/student_club/main/student_club.duckdb"
    _path = "data/dev_databases/student_club/student_club.sqlite"
    _row_count = 113
    _col_replace = {}

    major_id: t.String(nullable=True) = Field(description='''A unique identifier for each major''', primary_key=True)
    major_name: t.String(nullable=True) = Field(description='''major name''')
    department: t.String(nullable=True) = Field(description='''The name of the department that offers the major''')
    college: t.String(nullable=True) = Field(description='''The name college that houses the department that offers the major''')

