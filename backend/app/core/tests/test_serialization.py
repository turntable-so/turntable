import pytest

from app.core.serialization import bootstrap_project_from_dict
from app.models import Resource


@pytest.mark.django_db
@pytest.mark.skip(reason="need to fix")
def test_serialization():
    resource = Resource.objects.create(
        name="local_filesystem",
        type="File",
        config={"path": "data/csvs"},
    )
    repository = None

    defs_dict = {
        "resources": [
            {
                "resource": Resource.objects.get(
                    id=resource.id, repository__id=repository.id
                ),
            }
        ],
        "sources": [
            {
                "repository_id": repository.id,
                "name": "Test",
                "unique_name": "local_filesystemtest",
                "config": {
                    "table": "test",
                    "path": "data/csvs/test.csv",
                    "row_count": 28512,
                    "columns": {
                        "id": {"type": "int64"},
                        "date": {"type": "date"},
                        "store_nbr": {"type": "int64"},
                        "family": {"type": "string"},
                        "onpromotion": {"type": "int64"},
                    },
                    "_col_replace": {},
                },
            }
        ],
        "models": [
            {
                "name": "test",
                "unique_name": "test",
                "repository_id": repository.id,
                "read_only": False,
                "config": {
                    "deps": {"t": "local_filesystemtest"},
                    "steps": [
                        {
                            "type": "SQL",
                            "sql": "SELECT * FROM ts",
                            "sources": {"ts": "t"},
                            "output": "tt",
                        },
                        {
                            "type": "SQL",
                            "sql": "SELECT * FROM tt",
                            "sources": {"tt": "tt"},
                            "output": "ttt",
                        },
                        {"type": "Return", "input": "ttt"},
                    ],
                },
            }
        ],
    }

    proj = bootstrap_project_from_dict(defs_dict)
    sqlproj = proj.get_sql_project()
    sqlproj.optimize()
    sqlproj.get_lineage()
    lineage = sqlproj.stitch_lineage()
    assert lineage != {}
