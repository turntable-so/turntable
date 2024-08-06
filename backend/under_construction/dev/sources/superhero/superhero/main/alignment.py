# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import superhero # noqa F401 


@source(resource=superhero)
class Alignment:
    _table = "alignment"
    _unique_name = "superhero.superhero.main.Alignment"
    _schema = "main"
    _database = "superhero"
    _twin_path = "data/superhero/main/superhero.duckdb"
    _path = "data/dev_databases/superhero/superhero.sqlite"
    _row_count = 4
    _col_replace = {}

    id: t.Int64(nullable=False) = Field(description='''the unique identifier of the alignment''', primary_key=True)
    alignment: t.String(nullable=True) = Field(description='''the alignment of the superhero. Additional context: 
Alignment refers to a character's moral and ethical stance and can be used to describe the overall attitude or behavior of a superhero. Some common alignments for superheroes include:
Good: These superheroes are typically kind, selfless, and dedicated to protecting others and upholding justice. Examples of good alignments include Superman, Wonder Woman, and Spider-Man.
Neutral: These superheroes may not always prioritize the greater good, but they are not necessarily evil either. They may act in their own self-interest or make decisions based on their own moral code. Examples of neutral alignments include the Hulk and Deadpool.
	Bad: These superheroes are typically selfish, manipulative, and willing to harm others in pursuit of their own goals. Examples of evil alignments include Lex Luthor and the Joker.''')

