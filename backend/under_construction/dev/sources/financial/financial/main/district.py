# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import financial # noqa F401 


@source(resource=financial)
class District:
    _table = "district"
    _unique_name = "financial.financial.main.District"
    _schema = "main"
    _database = "financial"
    _twin_path = "data/financial/main/financial.duckdb"
    _path = "data/dev_databases/financial/financial.sqlite"
    _row_count = 77
    _col_replace = {}

    district_id: t.Int64(nullable=False) = Field(description='''location of branch''')
    A2: t.String(nullable=False) = Field(description='''district_name''')
    A3: t.String(nullable=False) = Field(description='''region''')
    A4: t.String(nullable=False)
    A5: t.String(nullable=False) = Field(description='''municipality < district < region''')
    A6: t.String(nullable=False) = Field(description='''municipality < district < region''')
    A7: t.String(nullable=False) = Field(description='''municipality < district < region''')
    A8: t.Int64(nullable=False) = Field(description='''municipality < district < region''')
    A9: t.Int64(nullable=False) = Field(description='''nan. Additional context: not useful''')
    A10: t.Float64(nullable=False) = Field(description='''ratio of urban inhabitants''')
    A11: t.Int64(nullable=False) = Field(description='''average salary''')
    A12: t.Float64(nullable=True) = Field(description='''unemployment rate 1995''')
    A13: t.Float64(nullable=False) = Field(description='''unemployment rate 1996''')
    A14: t.Int64(nullable=False) = Field(description='''no. of entrepreneurs per 1000 inhabitants''')
    A15: t.Int64(nullable=True) = Field(description='''no. of committed crimes 1995''')
    A16: t.Int64(nullable=False) = Field(description='''no. of committed crimes 1996''')

