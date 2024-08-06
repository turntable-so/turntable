from vega_datasets import data

if __name__ == "__main__":
    examples_class_path = "vinyl/examples.py"

    with open(examples_class_path, "w") as f:
        f.write("""
import os

import ibis

from vinyl.lib.table import VinylTable


def _return_vinyl_table(cls):
    def wrapper(*args, **kwargs) -> VinylTable:
        adj_path_base = os.path.dirname(os.path.dirname(__file__))
        return VinylTable(
            ibis.read_parquet(
                os.path.join(adj_path_base, cls.path), table_name=cls.__name__
            )._arg
        )
            
    wrapper.description = cls.description
    wrapper.references = cls.references

    return wrapper

class ExampleDataset:
    description: str
    references: str
    path: str

""")

    for dataset in dir(data):
        obj = getattr(data, dataset)
        path = f"vinyl/data/{dataset}.parquet"
        try:
            df = obj()
            df.to_parquet(path)
        except Exception:
            # file is not a dataframe
            continue

        if dataset[0].isdigit():
            dataset = f"_{dataset}"
        with open(examples_class_path, "a") as f:
            f.write(f"""
@_return_vinyl_table
class {dataset}(ExampleDataset):
    description = '''{obj.description}'''
    references = {obj.references}
    path = "vinyl/data/{dataset}.parquet"
    """)
