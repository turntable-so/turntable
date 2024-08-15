import os
from typing import Any, Callable

import ibis
from ibis.common.exceptions import IbisError

from vinyl.lib.connect import DatabaseFileConnector, _DatabaseConnector, _TableConnector
from vinyl.lib.constants import PreviewHelper
from vinyl.lib.field import Field
from vinyl.lib.settings import _load_project_module
from vinyl.lib.table import VinylTable


def _get_twin_relative_path(name: str, *subdirs) -> str:
    return os.path.join(
        "data",
        *subdirs,
        f"{name}.duckdb",
    )


def source(resource: Callable[..., Any], sample_row_count: int | None = 1000):
    def decorator(cls) -> VinylTable:
        connector = resource()

        schema = []
        for name, attr in cls.__annotations__.items():
            schema.append((name, attr))

        ibis_table = ibis.table(schema, name=cls._unique_name)
        table = VinylTable._create_from_schema(
            ibis.Schema.from_tuples(schema), cls._unique_name
        )
        parent_name = ".".join(cls.__module__.split(".")[2:])

        table._is_vinyl_source = True  # helps find sources in the project for Defs
        table._source_class = cls

        unbounded_op = table.tbl.op()
        if cls._col_replace != {}:
            table._col_replace = {unbounded_op: cls._col_replace}
        else:
            table._col_replace = {}

        if isinstance(connector, _DatabaseConnector):
            # declare here instead of in `full_connection` to avoid cls recursion
            db_conn = str(cls._database)
            schema_conn = str(cls._schema)
            table_conn = str(cls._table)

            def full_connection():
                return connector._get_table(
                    database=db_conn, schema=schema_conn, table=table_conn
                ).op()

            if PreviewHelper._preview == "full":
                table._conn_replace = {unbounded_op: full_connection}
            elif PreviewHelper._preview == "twin":
                # get twin
                module_path = _load_project_module().__file__
                if module_path is None:
                    raise ValueError(
                        "Unable to find the module path for the current project"
                    )
                twin_conn = DatabaseFileConnector(
                    os.path.join(
                        os.path.dirname(module_path),
                        _get_twin_relative_path(resource.__name__),
                    )
                )

                try:
                    table._twin_conn_replace = {
                        unbounded_op: lambda: twin_conn._get_table(
                            database=twin_conn._database,
                            schema=cls._schema,
                            table=cls._table,
                        ).op()
                    }
                except IbisError:
                    # twin doesn't exist, fall back to full conn, but not connected yet
                    table._conn_replace = {unbounded_op: full_connection}

            else:
                raise ValueError(
                    f"Invalid value for PreviewHelper.preview: {PreviewHelper._preview}"
                )
        elif isinstance(connector, _TableConnector):
            # declare here instead of in `full_connection` to avoid cls recursion
            path_conn = str(cls._path)

            def full_connection():
                # for file connectors, we reconnect to the individual file to get the correct table. Since these tables are not in memory, we need to read to get the location.
                adj_conn = type(connector)(path_conn)
                adj_conn._connect()
                tbl_for_op = next(iter(adj_conn._tbls.values()))
                return tbl_for_op.op()

            if PreviewHelper._preview == "full":
                table._conn_replace = {unbounded_op: full_connection}

            elif PreviewHelper._preview == "twin":
                try:
                    table._twin_conn_replace = {
                        unbounded_op: table.tbl.filter(
                            ibis.random()
                            < ibis.least(sample_row_count / cls._row_count, 1)
                        ).op()
                    }
                except IbisError:
                    # twin doesn't exist, fall back to full conn, but not connected yet
                    table._conn_replace = {unbounded_op: full_connection}
        else:
            raise NotImplementedError(
                f"Connector type {type(connector)} is not yet supported"
            )

        for name, attr in cls.__annotations__.items():
            field = Field(
                name=name,
                type=attr,
                parent_ibis_table=ibis_table,
                parent_name=parent_name,
            )
            if hasattr(cls, name):
                current: Field = getattr(cls, name)
                # Field info overrides the class level attributes, may want to change
                field._update(**current.asdict())
            setattr(cls, name, field)

        # update parent table to include the full set of annotations and save graph
        for name, attr in cls.__annotations__.items():
            current = getattr(cls, name)
            # Field info overrides the class level attributes, may want to change
            current._update(**{"parent_vinyl_table": table})

            # Make sure primary key col is set to unique even if user doesn't specify
            if current.primary_key:
                current.unique = True
            setattr(cls, name, current)
            current._update_source_class()
            # make sure final tbl (with source connections) is available for relations graph before storing
            current._store_source_adj_tbl(table)
            current._store_relations()

        return table

    return decorator
