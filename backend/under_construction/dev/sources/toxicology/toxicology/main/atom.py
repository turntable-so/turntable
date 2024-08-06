# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import toxicology # noqa F401 


@source(resource=toxicology)
class Atom:
    _table = "atom"
    _unique_name = "toxicology.toxicology.main.Atom"
    _schema = "main"
    _database = "toxicology"
    _twin_path = "data/toxicology/main/toxicology.duckdb"
    _path = "data/dev_databases/toxicology/toxicology.sqlite"
    _row_count = 12333
    _col_replace = {}

    atom_id: t.String(nullable=False) = Field(description='''the unique id of atoms''', primary_key=True)
    molecule_id: t.String(nullable=True) = Field(description='''identifying the molecule to which the atom belongs. Additional context: 
TRXXX_i represents ith atom of molecule TRXXX''', foreign_key=('Molecule', 'molecule_id'))
    element: t.String(nullable=True) = Field(description='''the element of the toxicology . Additional context:  cl: chlorine
 c: carbon
 h: hydrogen
 o: oxygen
 s: sulfur
 n: nitrogen
 p: phosphorus
 na: sodium
 br: bromine
 f: fluorine
 i: iodine
 sn: Tin
 pb: lead
 te: tellurium
 ca: Calcium''')

