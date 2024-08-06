# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import superhero # noqa F401 


@source(resource=superhero)
class Superhero:
    _table = "superhero"
    _unique_name = "superhero.superhero.main.Superhero"
    _schema = "main"
    _database = "superhero"
    _twin_path = "data/superhero/main/superhero.duckdb"
    _path = "data/dev_databases/superhero/superhero.sqlite"
    _row_count = 750
    _col_replace = {}

    id: t.Int64(nullable=False) = Field(description='''the unique identifier of the superhero''', primary_key=True)
    superhero_name: t.String(nullable=True) = Field(description='''the name of the superhero''')
    full_name: t.String(nullable=True) = Field(description='''the full name of the superhero. Additional context: 
The full name of a person typically consists of their given name, also known as their first name or personal name, and their surname, also known as their last name or family name. For example, if someone's given name is "John" and their surname is "Smith," their full name would be "John Smith."''')
    gender_id: t.Int64(nullable=True) = Field(description='''the id of the superhero's gender''', foreign_key=('Gender', 'id'))
    eye_colour_id: t.Int64(nullable=True) = Field(description='''the id of the superhero's eye color''', foreign_key=('Colour', 'id'))
    hair_colour_id: t.Int64(nullable=True) = Field(description='''the id of the superhero's hair color''', foreign_key=('Colour', 'id'))
    skin_colour_id: t.Int64(nullable=True) = Field(description='''the id of the superhero's skin color''', foreign_key=('Colour', 'id'))
    race_id: t.Int64(nullable=True) = Field(description='''the id of the superhero's race''', foreign_key=('Race', 'id'))
    publisher_id: t.Int64(nullable=True) = Field(description='''the id of the publisher''', foreign_key=('Publisher', 'id'))
    alignment_id: t.Int64(nullable=True) = Field(description='''the id of the superhero's alignment''', foreign_key=('Alignment', 'id'))
    height_cm: t.Int64(nullable=True) = Field(description='''the height of the superhero. Additional context: 
The unit of height is centimeter. If the height_cm is NULL or 0, it means the height of the superhero is missing. ''')
    weight_kg: t.Int64(nullable=True) = Field(description='''the weight of the superhero. Additional context: 
The unit of weight is kilogram. If the weight_kg is NULL or 0, it means the weight of the superhero is missing.''')

