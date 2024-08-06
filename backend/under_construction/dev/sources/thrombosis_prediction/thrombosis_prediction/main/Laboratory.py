# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import thrombosis_prediction # noqa F401 


@source(resource=thrombosis_prediction)
class Laboratory:
    _table = "Laboratory"
    _unique_name = "thrombosis_prediction.thrombosis_prediction.main.Laboratory"
    _schema = "main"
    _database = "thrombosis_prediction"
    _twin_path = "data/thrombosis_prediction/main/thrombosis_prediction.duckdb"
    _path = "data/dev_databases/thrombosis_prediction/thrombosis_prediction.sqlite"
    _row_count = 13908
    _col_replace = {"T_BIL": "T-BIL", "T_CHO": "T-CHO", "U_PRO": "U-PRO", "DNA_II": "DNA-II"}

    ID: t.Int64(nullable=False) = Field(description='''identification of the patient''', foreign_key=('Patient', 'ID'))
    Date: t.Date(nullable=False) = Field(description='''Date of the laboratory tests (YYMMDD)''')
    GOT: t.Int64(nullable=True) = Field(description='''AST glutamic oxaloacetic transaminase. Additional context: Commonsense evidence:

Normal range: N < 60''')
    GPT: t.Int64(nullable=True) = Field(description='''ALT glutamic pyruvic transaminase. Additional context: Commonsense evidence:

Normal range: N < 60''')
    LDH: t.Int64(nullable=True) = Field(description='''lactate dehydrogenase. Additional context: Commonsense evidence:

Normal range: N < 500''')
    ALP: t.Int64(nullable=True) = Field(description='''alkaliphophatase. Additional context: Commonsense evidence:

Normal range: N < 300''')
    TP: t.Float64(nullable=True) = Field(description='''total protein. Additional context: Commonsense evidence:

Normal range: 6.0 < N < 8.5''')
    ALB: t.Float64(nullable=True) = Field(description='''albumin. Additional context: Commonsense evidence:

Normal range: 3.5 < N < 5.5''')
    UA: t.Float64(nullable=True) = Field(description='''uric acid. Additional context: Commonsense evidence:

Normal range: N > 8.0 (Male)N > 6.5 (Female)''')
    UN: t.Int64(nullable=True) = Field(description='''urea nitrogen. Additional context: Commonsense evidence:

Normal range: N < 30''')
    CRE: t.Float64(nullable=True) = Field(description='''creatinine. Additional context: Commonsense evidence:

Normal range: N < 1.5''')
    T_BIL: t.Float64(nullable=True) = Field(description='''total bilirubin. Additional context: Commonsense evidence:

Normal range: N < 2.0''')
    T_CHO: t.Int64(nullable=True) = Field(description='''total cholesterol. Additional context: Commonsense evidence:
Normal range: N < 250''')
    TG: t.Int64(nullable=True) = Field(description='''triglyceride. Additional context: Commonsense evidence:

Normal range: N < 200''')
    CPK: t.Int64(nullable=True) = Field(description='''creatinine phosphokinase. Additional context: Commonsense evidence:
Normal range: N < 250''')
    GLU: t.Int64(nullable=True) = Field(description='''blood glucose. Additional context: Commonsense evidence:
Normal range: N < 180''')
    WBC: t.Float64(nullable=True) = Field(description='''White blood cell. Additional context: Commonsense evidence:
Normal range: 3.5 < N < 9.0''')
    RBC: t.Float64(nullable=True) = Field(description='''Red blood cell. Additional context: Commonsense evidence:

Normal range: 3.5 < N < 6.0''')
    HGB: t.Float64(nullable=True) = Field(description='''Hemoglobin. Additional context: Commonsense evidence:

Normal range: 10 < N < 17''')
    HCT: t.Float64(nullable=True) = Field(description='''Hematoclit. Additional context: Commonsense evidence:
Normal range: 29 < N < 52''')
    PLT: t.Int64(nullable=True) = Field(description='''platelet. Additional context: Commonsense evidence:

Normal range: 100 < N < 400''')
    PT: t.Float64(nullable=True) = Field(description='''prothrombin time. Additional context: Commonsense evidence:

Normal range: N < 14''')
    APTT: t.Int64(nullable=True) = Field(description='''activated partial prothrombin time. Additional context: Commonsense evidence:

Normal range: N < 45''')
    FG: t.Float64(nullable=True) = Field(description='''fibrinogen. Additional context: Commonsense evidence:

Normal range: 150 < N < 450''')
    PIC: t.Int64(nullable=True)
    TAT: t.Int64(nullable=True)
    TAT2: t.Int64(nullable=True)
    U_PRO: t.String(nullable=True) = Field(description='''proteinuria. Additional context: Commonsense evidence:

Normal range: 0 < N < 30''')
    IGG: t.Int64(nullable=True) = Field(description='''Ig G. Additional context: Commonsense evidence:

Normal range: 900 < N < 2000''')
    IGA: t.Int64(nullable=True) = Field(description='''Ig A. Additional context: Commonsense evidence:

Normal range: 80 < N < 500''')
    IGM: t.Int64(nullable=True) = Field(description='''Ig M. Additional context: Commonsense evidence:

Normal range: 40 < N < 400''')
    CRP: t.String(nullable=True) = Field(description='''C-reactive protein. Additional context: Commonsense evidence:

Normal range: N= -, +-, or N < 1.0''')
    RA: t.String(nullable=True) = Field(description='''Rhuematoid Factor. Additional context: Commonsense evidence:

Normal range: N= -, +-''')
    RF: t.String(nullable=True) = Field(description='''RAHA. Additional context: Commonsense evidence:

Normal range: N < 20''')
    C3: t.Int64(nullable=True) = Field(description='''complement 3. Additional context: Commonsense evidence:

Normal range: N > 35''')
    C4: t.Int64(nullable=True) = Field(description='''complement 4. Additional context: Commonsense evidence:

Normal range: N > 10''')
    RNP: t.String(nullable=True) = Field(description='''anti-ribonuclear protein. Additional context: Commonsense evidence:

Normal range: N= -, +-''')
    SM: t.String(nullable=True) = Field(description='''anti-SM. Additional context: Commonsense evidence:

Normal range: N= -, +-''')
    SC170: t.String(nullable=True) = Field(description='''anti-scl70. Additional context: Commonsense evidence:

Normal range: N= -, +-''')
    SSA: t.String(nullable=True) = Field(description='''anti-SSA. Additional context: Commonsense evidence:

Normal range: N= -, +-''')
    SSB: t.String(nullable=True) = Field(description='''anti-SSB. Additional context: Commonsense evidence:

Normal range: N= -, +-''')
    CENTROMEA: t.String(nullable=True) = Field(description='''anti-centromere. Additional context: Commonsense evidence:

Normal range: N= -, +-''')
    DNA: t.String(nullable=True) = Field(description='''anti-DNA. Additional context: Commonsense evidence:

Normal range: N < 8''')
    DNA_II: t.Int64(nullable=True) = Field(description='''anti-DNA. Additional context: Commonsense evidence:

Normal range: N < 8''')

