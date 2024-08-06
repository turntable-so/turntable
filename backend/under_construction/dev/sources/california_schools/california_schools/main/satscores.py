# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import california_schools # noqa F401 


@source(resource=california_schools)
class Satscores:
    _table = "satscores"
    _unique_name = "california_schools.california_schools.main.Satscores"
    _schema = "main"
    _database = "california_schools"
    _twin_path = "data/california_schools/main/california_schools.duckdb"
    _path = "data/dev_databases/california_schools/california_schools.sqlite"
    _row_count = 2269
    _col_replace = {}

    cds: t.String(nullable=False) = Field(description='''California Department Schools''', foreign_key=('Schools', 'CDSCode'), unique = True)
    rtype: t.String(nullable=False) = Field(description='''rtype. Additional context: unuseful''')
    sname: t.String(nullable=True) = Field(description='''school name''')
    dname: t.String(nullable=True) = Field(description='''district segment''')
    cname: t.String(nullable=True) = Field(description='''county name''')
    enroll12: t.Int64(nullable=False) = Field(description='''enrollment (1st-12nd grade)''')
    NumTstTakr: t.Int64(nullable=False) = Field(description='''Number of Test Takers in this school. Additional context: number of test takers in each school''')
    AvgScrRead: t.Int64(nullable=True) = Field(description='''average scores in Reading. Additional context: average scores in Reading''')
    AvgScrMath: t.Int64(nullable=True) = Field(description='''average scores in Math. Additional context: average scores in Math''')
    AvgScrWrite: t.Int64(nullable=True) = Field(description='''average scores in writing. Additional context: average scores in writing''')
    NumGE1500: t.Int64(nullable=True) = Field(description='''Number of Test Takers Whose Total SAT Scores Are Greater or Equal to 1500. Additional context: Number of Test Takers Whose Total SAT Scores Are Greater or Equal to 1500



Excellence Rate = NumGE1500 / NumTstTakr''')

