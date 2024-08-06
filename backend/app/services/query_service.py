from vinyl.lib.definitions import _load_project_defs
import importlib.util


class QueryService:
    @staticmethod
    def query(query_payload):
        defs = _load_project_defs()
        query_payload.sql
