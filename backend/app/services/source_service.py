from vinyl.lib.definitions import _load_project_defs
from itertools import groupby
import importlib.util
import json


class SourceService:
    @staticmethod
    def get_sources(defs):
        sources = []
        try:
            for source in defs.sources:
                sources.append(
                    {
                        "database": source._source_class._database,
                        "schema": source._source_class._schema,
                        "table": source._source_class._table,
                        "id": source._source_class._unique_name,
                        "sql": source.limit(1000).to_sql(),
                        "records": [],
                    }
                )
        except Exception as e:
            print(e)

        return sources

    @staticmethod
    def get_resource(defs, database_name: str):
        resource = [
            resource
            for resource in defs.resources
            if resource()._database == database_name
        ][0]
        return resource()

    @staticmethod
    def get_table(id: str):
        table = "transactions_1k"
        defs = _load_project_defs()
        table = [
            source for source in defs.sources if source._source_class._unique_name == id
        ][0]
        return table
