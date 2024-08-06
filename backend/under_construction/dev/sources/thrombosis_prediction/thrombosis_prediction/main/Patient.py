# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import thrombosis_prediction # noqa F401 


@source(resource=thrombosis_prediction)
class Patient:
    _table = "Patient"
    _unique_name = "thrombosis_prediction.thrombosis_prediction.main.Patient"
    _schema = "main"
    _database = "thrombosis_prediction"
    _twin_path = "data/thrombosis_prediction/main/thrombosis_prediction.duckdb"
    _path = "data/dev_databases/thrombosis_prediction/thrombosis_prediction.sqlite"
    _row_count = 1238
    _col_replace = {"First_Date": "First Date"}

    ID: t.Int64(nullable=False) = Field(description='''identification of the patient''', primary_key=True)
    SEX: t.String(nullable=True) = Field(description='''Sex. Additional context: F: female; M: male''')
    Birthday: t.Date(nullable=True) = Field(description='''Birthday''')
    Description: t.Date(nullable=True) = Field(description='''the first date when a patient data was recorded. Additional context: null or empty: not recorded''')
    First_Date: t.Date(nullable=True) = Field(description='''the date when a patient came to the hospital''')
    Admission: t.String(nullable=True) = Field(description='''patient was admitted to the hospital (+) or followed at the outpatient clinic (-). Additional context: patient was admitted to the hospital (+) or followed at the outpatient clinic (-)''')
    Diagnosis: t.String(nullable=True) = Field(description='''disease names''')

