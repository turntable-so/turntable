# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import student_club # noqa F401 


@source(resource=student_club)
class ZipCode:
    _table = "zip_code"
    _unique_name = "student_club.student_club.main.ZipCode"
    _schema = "main"
    _database = "student_club"
    _twin_path = "data/student_club/main/student_club.duckdb"
    _path = "data/dev_databases/student_club/student_club.sqlite"
    _row_count = 41877
    _col_replace = {}

    zip_code: t.Int64(nullable=True) = Field(description='''The ZIP code itself. A five-digit number identifying a US post office.''', primary_key=True)
    type: t.String(nullable=True) = Field(description='''The kind of ZIP code. Additional context:  
� Standard: the normal codes with which most people are familiar 
� PO Box: zip codes have post office boxes 
� Unique: zip codes that are assigned to individual organizations.''')
    city: t.String(nullable=True) = Field(description='''The city to which the ZIP pertains''')
    county: t.String(nullable=True) = Field(description='''The county to which the ZIP pertains''')
    state: t.String(nullable=True) = Field(description='''The name of the state to which the ZIP pertains''')
    short_state: t.String(nullable=True) = Field(description='''The abbreviation of the state to which the ZIP pertains''')

