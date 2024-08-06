# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import thrombosis_prediction # noqa F401 


@source(resource=thrombosis_prediction)
class Examination:
    _table = "Examination"
    _unique_name = "thrombosis_prediction.thrombosis_prediction.main.Examination"
    _schema = "main"
    _database = "thrombosis_prediction"
    _twin_path = "data/thrombosis_prediction/main/thrombosis_prediction.duckdb"
    _path = "data/dev_databases/thrombosis_prediction/thrombosis_prediction.sqlite"
    _row_count = 806
    _col_replace = {"Examination_Date": "Examination Date", "aCL_IgG": "aCL IgG", "aCL_IgM": "aCL IgM", "ANA_Pattern": "ANA Pattern", "aCL_IgA": "aCL IgA"}

    ID: t.Int64(nullable=True) = Field(description='''identification of the patient''', foreign_key=('Patient', 'ID'))
    Examination_Date: t.Date(nullable=True) = Field(description='''Examination Date''')
    aCL_IgG: t.Float64(nullable=True) = Field(description='''anti-Cardiolipin antibody (IgG) concentration''')
    aCL_IgM: t.Float64(nullable=True) = Field(description='''anti-Cardiolipin antibody (IgM) concentration''')
    ANA: t.Int64(nullable=True) = Field(description='''anti-nucleus antibody concentration''')
    ANA_Pattern: t.String(nullable=True) = Field(description='''pattern observed in the sheet of ANA examination''')
    aCL_IgA: t.Int64(nullable=True) = Field(description='''anti-Cardiolipin antibody (IgA) concentration''')
    Diagnosis: t.String(nullable=True) = Field(description='''disease names''')
    KCT: t.String(nullable=True) = Field(description='''measure of degree of coagulation. Additional context: +: positive

-: negative''')
    RVVT: t.String(nullable=True) = Field(description='''measure of degree of coagulation. Additional context: +: positive

-: negative''')
    LAC: t.String(nullable=True) = Field(description='''measure of degree of coagulation. Additional context: +: positive

-: negative''')
    Symptoms: t.String(nullable=True) = Field(description='''other symptoms observed''')
    Thrombosis: t.Int64(nullable=True) = Field(description='''degree of thrombosis. Additional context: 0: negative (no thrombosis)
1: positive (the most severe one)
2: positive (severe)3: positive (mild)''')

