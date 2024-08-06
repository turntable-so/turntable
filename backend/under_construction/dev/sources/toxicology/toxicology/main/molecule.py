# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import toxicology # noqa F401 


@source(resource=toxicology)
class Molecule:
    _table = "molecule"
    _unique_name = "toxicology.toxicology.main.Molecule"
    _schema = "main"
    _database = "toxicology"
    _twin_path = "data/toxicology/main/toxicology.duckdb"
    _path = "data/dev_databases/toxicology/toxicology.sqlite"
    _row_count = 343
    _col_replace = {}

    molecule_id: t.String(nullable=False) = Field(description='''unique id of molecule. Additional context: "+" --> this molecule / compound is carcinogenic
'-' this molecule is not / compound carcinogenic''', primary_key=True)
    label: t.String(nullable=True) = Field(description='''whether this molecule is carcinogenic or not''')

