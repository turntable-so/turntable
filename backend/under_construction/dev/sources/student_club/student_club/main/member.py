# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import student_club # noqa F401 


@source(resource=student_club)
class Member:
    _table = "member"
    _unique_name = "student_club.student_club.main.Member"
    _schema = "main"
    _database = "student_club"
    _twin_path = "data/student_club/main/student_club.duckdb"
    _path = "data/dev_databases/student_club/student_club.sqlite"
    _row_count = 33
    _col_replace = {}

    member_id: t.String(nullable=True) = Field(description='''unique id of member''', primary_key=True)
    first_name: t.String(nullable=True) = Field(description='''member's first name''')
    last_name: t.String(nullable=True) = Field(description='''member's last name. Additional context:  
full name is first_name + last_name. e.g. A member's first name is Angela and last name is Sanders. Thus, his/her full name is Angela Sanders.''')
    email: t.String(nullable=True) = Field(description='''member's email''')
    position: t.String(nullable=True) = Field(description='''The position the member holds in the club''')
    t_shirt_size: t.String(nullable=True) = Field(description='''The size of tee shirt that member wants when shirts are ordered. Additional context:  usually the student ordered t-shirt with lager size has bigger body shape ''')
    phone: t.String(nullable=True) = Field(description='''The best telephone at which to contact the member''')
    zip: t.Int64(nullable=True) = Field(description='''the zip code of the member's hometown''', foreign_key=('ZipCode', 'zip_code'))
    link_to_major: t.String(nullable=True) = Field(description='''The unique identifier of the major of the member. References the Major table''', foreign_key=('Major', 'major_id'))

