# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import toxicology # noqa F401 


@source(resource=toxicology)
class Bond:
    _table = "bond"
    _unique_name = "toxicology.toxicology.main.Bond"
    _schema = "main"
    _database = "toxicology"
    _twin_path = "data/toxicology/main/toxicology.duckdb"
    _path = "data/dev_databases/toxicology/toxicology.sqlite"
    _row_count = 12379
    _col_replace = {}

    bond_id: t.String(nullable=False) = Field(description='''unique id representing bonds. Additional context: TRxxx_A1_A2:
TRXXX refers to which molecule
A1 and A2 refers to which atom''', primary_key=True)
    molecule_id: t.String(nullable=True) = Field(description='''identifying the molecule in which the bond appears''', foreign_key=('Molecule', 'molecule_id'))
    bond_type: t.String(nullable=True) = Field(description='''type of the bond. Additional context: 
-: single bond
'=': double bond
'#': triple bond''')

