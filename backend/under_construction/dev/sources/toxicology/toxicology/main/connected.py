# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import toxicology # noqa F401 


@source(resource=toxicology)
class Connected:
    _table = "connected"
    _unique_name = "toxicology.toxicology.main.Connected"
    _schema = "main"
    _database = "toxicology"
    _twin_path = "data/toxicology/main/toxicology.duckdb"
    _path = "data/dev_databases/toxicology/toxicology.sqlite"
    _row_count = 24758
    _col_replace = {}

    atom_id: t.String(nullable=False) = Field(description='''id of the first atom''', foreign_key=('Atom', 'atom_id'))
    atom_id2: t.String(nullable=False) = Field(description='''id of the second atom''')
    bond_id: t.String(nullable=True) = Field(description='''bond id representing bond between two atoms''', foreign_key=('Bond', 'bond_id'))

