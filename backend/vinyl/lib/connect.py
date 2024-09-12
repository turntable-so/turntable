from __future__ import annotations

import itertools
import json
import os
import secrets
import traceback
from abc import ABC, abstractmethod
from argparse import Namespace
from contextlib import closing
from dataclasses import asdict, dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional

import ibis
import ibis.expr.types as ir
import pandas as pd
from ibis import Schema
from ibis.backends import BaseBackend
from ibis.backends.duckdb import Backend as DuckDBBackend
from mpire import WorkerPool
from tqdm import tqdm

from vinyl.lib.db_methods import ValidationOutput
from vinyl.lib.dbt import DBTProject
from vinyl.lib.dbt_methods import DBTDialect, DBTVersion
from vinyl.lib.errors import VinylError, VinylErrorType
from vinyl.lib.utils.pkg import _get_project_directory
from vinyl.lib.utils.text import (
    _extract_uri_scheme,
    _generate_random_ascii_string,
)

_TEMP_PATH_PREFIX = "vinyl_"
_QUERY_LIMIT = 100000
_JOIN_STRING_HELPER = "_____"
_PARALLEL_DB_THREADS = 10

# NOTE: Starting in Ibis 10.0, Ibis now uses nomenclature for tables (i.e. catalog, database, name), that is distinct from how we usually think about it. Database, schema, name. Until we rename our variables, the variable naming will be confusing.


@dataclass
class SourceInfo:
    _name: str
    _location: str
    _schema: Schema | None
    _parent_resource: Any | None = None


class _ResourceConnector(ABC):
    """Base interface for handling connecting to resource and getting sources"""

    @abstractmethod
    def _list_sources(
        self, with_schema=False
    ) -> tuple[list[SourceInfo], list[VinylError]]:
        pass

    @abstractmethod
    def _connect(self) -> BaseBackend:
        pass

    @abstractmethod
    def sql_to_df(self, query: str, limit: int | None) -> pd.DataFrame:
        pass

    @abstractmethod
    def validate_sql(self, query: str) -> ValidationOutput:
        pass

    def _get_name(self):
        return self.__class__.__name__.replace("Connector", "").lower()


# exists to help distinguish between table and database connectors
class _TableConnector(_ResourceConnector):
    _tbls: dict[str, ir.Table]
    _path: str

    def __init__(self, path: str):
        self._path = path

    def _get_table(self, path) -> ir.Table:
        # for file connectors, we reconnect to the individual file to get the correct table. Since these tables are not in memory, we need to read to get the location.
        adj_conn = self.__class__(path)
        adj_conn._connect()
        return next(iter(adj_conn._tbls.values()))

    def _generate_twin(self, path, sample_row_count=1000) -> ir.Table:
        tbl = self._get_table(path)
        row_count = tbl.count()
        sampled = tbl.filter(
            ibis.random() < ibis.least(sample_row_count / row_count, 1)
        )
        return sampled

    def sql_to_df(self, query: str, limit: int | None = _QUERY_LIMIT) -> pd.DataFrame:
        pass

    def validate_sql(self, query: str) -> ValidationOutput:
        pass


class _DatabaseConnector(_ResourceConnector):
    _conn: BaseBackend
    _allows_multiple_databases: bool = True
    _allows_multiple_schemas: bool = True
    _tables: list[str]
    _excluded_dbs: list[str] = []
    _excluded_schemas: list[str] = []
    _excluded_tables: list[str] = []

    def _expand_table_names(self, location: str) -> list[str]:
        db, sch, table = location.split(_JOIN_STRING_HELPER)
        if table == "*":
            if (
                not self._allows_multiple_schemas
                and not self._allows_multiple_databases
            ):
                table_set = set(self._conn.list_tables())
            elif not self._allows_multiple_schemas:
                # likely won't work
                table_set = set(self._conn.list_tables(database=db))
            elif not self._allows_multiple_databases:
                table_set = set(self._conn.list_tables(database=sch))
            else:
                table_set = set(self._conn.list_tables(database=(db, sch)))

            adj_tables = list(table_set - set(self._excluded_tables))
        else:
            adj_tables = [table]

        adj_tables = [_JOIN_STRING_HELPER.join([db, sch, t]) for t in adj_tables]

        return adj_tables

    # Define the function that processes each item
    def _get_sources_for_table_names(
        self, pre: str, with_schema: bool
    ) -> tuple[SourceInfo | None, VinylError | None]:
        conn: BaseBackend = self._connect()
        db, sch, tbl = pre.split(_JOIN_STRING_HELPER)
        location = f"{db}.{sch}"
        full_location = f"{location}.{tbl}"

        try:
            if with_schema:
                ibis_table = None
                if (
                    not self._allows_multiple_databases
                    and not self._allows_multiple_schemas
                ):
                    ibis_table = conn.table(name=tbl)
                elif not self._allows_multiple_schemas:
                    ibis_table = conn.table(database=db, name=tbl)
                elif not self._allows_multiple_databases:
                    ibis_table = conn.table(database=sch, name=tbl)
                else:
                    ibis_table = conn.table(database=(db, sch), name=tbl)
            return SourceInfo(
                _name=tbl,
                _location=location,
                _schema=(ibis_table.schema() if with_schema else None),
            ), None
        except Exception as e:
            return None, VinylError(
                node_id=full_location,
                type=VinylErrorType.DATABASE_ERROR,
                dialect=None,
                msg=str(e),
                traceback=traceback.format_exc(),
            )

    def _find_sources_in_db(
        self,
        databases_override: list[str] | None = None,
        with_schema: bool = False,
    ) -> tuple[list[SourceInfo], list[VinylError]]:
        self._connect()

        expanded_table_names = []

        # get tables
        for loc in self._tables:
            split_ = loc.split(".")
            if len(split_) != 3:
                continue
            database, schema, table = split_
            if databases_override is not None:
                adj_databases = databases_override
            elif database == "*":
                if not hasattr(self._conn, "list_catalogs"):
                    raise ValueError(
                        f"Database specification required for this connector: {self.__class__.__name__}"
                    )
                adj_databases = list(
                    set(self._conn.list_catalogs()) - set(self._excluded_dbs)
                )
            else:
                adj_databases = [database]

            unadj_tbl_names = []
            for db in adj_databases:
                if not self._allows_multiple_schemas:
                    adj_schemas = ["main"]
                elif schema == "*":
                    schema_set = set(
                        self._conn.list_databases(catalog=db)
                        if self._allows_multiple_databases
                        else self._conn.list_databases()
                    )
                    adj_schemas = list(schema_set - set(self._excluded_schemas))
                else:
                    adj_schemas = [schema]

                for sch in adj_schemas:
                    unadj_tbl_names.append(_JOIN_STRING_HELPER.join([db, sch, table]))

        with WorkerPool(n_jobs=10, keep_alive=True) as pool:
            nested_table_names = list(
                tqdm(
                    pool.imap_unordered(self._expand_table_names, unadj_tbl_names),
                    total=len(unadj_tbl_names),
                    desc="Getting table names...",
                )
            )

        # flatten list
        expanded_table_names = list(itertools.chain(*nested_table_names))

        if with_schema:
            # make parallel calls to db
            with WorkerPool(n_jobs=10, keep_alive=True) as pool:
                results = list(
                    tqdm(
                        pool.imap_unordered(
                            self._get_sources_for_table_names,
                            [(pre, True) for pre in expanded_table_names],
                        ),
                        total=len(expanded_table_names),
                        desc="Getting table schemas if required...",
                    )
                )
        else:
            # no need to make parallel calls
            results = [
                self._get_sources_for_table_names(t, False)
                for t in expanded_table_names
            ]
        sources = [r[0] for r in results if r[0] is not None]
        errors = [r[1] for r in results if r[1] is not None]
        return sources, errors

    @classmethod
    def _create_twin_connection(cls, path: str) -> DuckDBBackend:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        return ibis.duckdb.connect(path)

    @lru_cache()
    def _get_table(self, database: str, schema: str, table: str) -> ir.Table:
        conn = self._connect()
        if not self._allows_multiple_databases and not self._allows_multiple_schemas:
            return conn.table(table)
        elif not self._allows_multiple_schemas:
            # likely won't work
            return conn.table(database=database, name=table)
        elif not self._allows_multiple_databases:
            return conn.table(database=schema, name=table)

        return conn.table(database=(database, schema), name=table)

    def _generate_twin(
        self,
        twin_path: str,
        database: str,
        schema: str,
        table: str,
        sample_row_count: int | None = 1000,
    ) -> ir.Table:
        tbl = self._get_table(database, schema, table)
        if sample_row_count is None:
            sampled = tbl
        else:
            row_count = tbl.count()
            # using safer random() sample
            sampled = tbl.filter(
                ibis.random() < ibis.least(sample_row_count / row_count, 1)
            )
        pyarrow_table = sampled.to_pyarrow()
        conn = self._create_twin_connection(twin_path)
        # using raw sql to set the schema since the argument is not supported in the ibis api

        # create final table
        conn.raw_sql(f"CREATE SCHEMA IF NOT EXISTS {schema}")
        conn.raw_sql(f"USE {schema}")
        table_temp_name = f"table_{secrets.token_hex(8)}"
        temp_table = conn.create_table(
            table_temp_name, obj=pyarrow_table, overwrite=True
        )

        # reconnect to catch type errors
        reconn = ibis.duckdb.connect(twin_path)
        temp_table = reconn.table(table_temp_name, schema=schema)
        original_types = sampled.schema().types
        cast_dict = {}
        for i, (name, type) in enumerate(temp_table.schema().items()):
            cast_dict[name] = original_types[i]
        temp_table = temp_table.cast(cast_dict)

        # create final table and delete temp one
        final_table = conn.create_table(table, obj=temp_table, overwrite=True)
        conn.drop_table(table_temp_name)
        return final_table

    def _sql_to_df_query_helper(
        self, query: str, limit: int | None = _QUERY_LIMIT
    ) -> str:
        alias = _generate_random_ascii_string(8)
        query = f"select * from ({query}) as {alias}"
        if limit:
            query += f" limit {limit}"
        return query

    def sql_to_df(self, query: str, limit: int | None = _QUERY_LIMIT) -> pd.DataFrame:
        conn = self._connect()
        query = self._sql_to_df_query_helper(query, limit)
        return conn.sql(query).execute()

    def validate_sql(self, query: str) -> ValidationOutput:
        pass


class _FileConnector(_ResourceConnector):
    _conn: DuckDBBackend = ibis.duckdb.connect()
    _paths_visited: list[str] = []
    _excluded_dbs = ["system", "temp"]
    _excluded_schemas = ["information_schema", "pg_catalog"]
    _remote: bool
    _path: str

    def __init__(self, path: str):
        if scheme := _extract_uri_scheme(path):
            import fsspec

            self._conn.register_filesystem(fsspec.filesystem(scheme))
            self._remote = True
            self._path = path
        else:
            self._remote = False
            # adjust local path so it works even if you are not in the root directory
            self._path = os.path.join(_get_project_directory(), path)


class DatabaseFileConnector(_FileConnector, _DatabaseConnector):
    _excluded_tables: list[str] = ["sqlite_sequence"]
    _use_sqlite: bool

    def __init__(
        self, path: str, tables: list[str] = ["*.*.*"], use_sqlite: bool = False
    ):
        super().__init__(
            path
        )  # init method from _FileConnector, not Database Connector (because of ordering)
        self._tables = tables
        if any([len(t.split(".")) != 3 for t in tables]):
            raise ValueError(
                "tables must be a string of format 'database.schema.table'"
            )
        self._use_sqlite = use_sqlite
        if use_sqlite:
            self._allows_multiple_databases = False
            self._allows_multiple_schemas = False

    def _list_sources(
        self, with_schema=False
    ) -> tuple[list[SourceInfo], list[VinylError]]:
        out, errors = self._find_sources_in_db(
            with_schema=with_schema, databases_override=[self._database]
        )
        return out, errors

    def _connect(self) -> DuckDBBackend:
        if self._use_sqlite:
            self._conn = self._connect_helper_sqlite(self._path)
            return self._conn
        return self._connect_helper_duckdb(self._conn, self._path)

    @classmethod
    @lru_cache()
    def _connect_helper_duckdb(cls, conn: DuckDBBackend, path) -> DuckDBBackend:
        # caching ensures we don't attach a database from the same path twice
        name = cls._get_db_name(path)
        if path.endswith(".duckdb") or path.endswith(".db"):
            conn.attach(path, name, read_only=os.getenv("VINYL_READ_ONLY", False))

        elif path.endswith(".sqlite"):
            conn.attach(
                path, name, read_only=os.getenv("VINYL_READ_ONLY", False), sqlite=True
            )

        else:
            raise NotImplementedError(
                f"Connection for {path} not supported. Only .duckdb and .sqlite files are supported."
            )

        return conn

    @property
    def _database(self) -> str:
        return self._get_db_name(self._path)

    @classmethod
    @lru_cache()
    def _get_db_name(cls, path):
        name = Path(path).stem
        # handle situation where two database files have the same stem name
        if name in cls._conn.list_catalogs():
            name += str(secrets.token_hex(8))
        return name

    @staticmethod
    @lru_cache()
    def _connect_helper_sqlite(path: str):
        conn = ibis.sqlite.connect(path)
        return conn


class FileConnector(_FileConnector, _TableConnector):
    _tbls: dict[str, ir.Table]

    def __init__(self, path: str):
        super().__init__(
            path
        )  # init method from p_FileConnector, not Database Connector (because of ordering)
        self._tbls: dict[str, ir.Table] = {}

    def _connect(self) -> DuckDBBackend:
        # caching ensures we don't attach a database from the same path twice
        self._tbls = self._connect_helper(self._conn, self._path)
        return self._conn

    def _list_sources(
        self, with_schema=False
    ) -> tuple[list[SourceInfo], list[VinylError]]:
        self._connect()
        return [
            SourceInfo(
                _name=tbl.get_name(),
                _location=path,
                _schema=tbl.schema() if with_schema else None,
            )
            for path, tbl in self._tbls.items()
        ], None

    @classmethod
    @lru_cache()
    def _connect_helper(cls, conn, path) -> dict[str, ir.Table]:
        stem = Path(path).stem
        tbls = {}
        # caching ensures we don't attach a database from the same path twice
        if path.endswith(".csv"):
            tbls[path] = conn.read_csv(path, table_name=stem)
        elif path.endswith(".parquet"):
            tbls[path] = conn.read_parquet(path, table_name=stem)
        elif path.endswith(".json"):
            tbls[path] = conn.read_json(path, table_name=stem)
        elif os.path.isdir(path):
            for sub in os.listdir(path):
                path_it = os.path.join(path, sub)
                # only looking at files prevents recursion into subdirectories
                if os.path.isfile(path_it) and not sub.startswith("."):
                    tbls.update(cls._connect_helper(conn, path_it))

        else:
            raise NotImplementedError(
                f"Connection for {path} not supported. Only .csv, .parquet, and .json files are supported"
            )

        return tbls


class BigQueryConnector(_DatabaseConnector):
    _credentials: Any
    _BQ_ITERATOR_ROW_CUTOFF = 1000  # faster to use iterators for small datasets, but faster to download directly for large datasets

    def __init__(
        self,
        tables: list[str],
        service_account_path: str | None = None,
        service_account_info: dict[str, str] | None = None,
    ):
        self._service_account_path = service_account_path
        self._service_account_info = service_account_info
        self._tables = tables

    def _connect(self) -> BaseBackend:
        self._conn = BigQueryConnector._connect_helper(
            self._service_account_path,
            json.dumps(self._service_account_info)
            if self._service_account_info
            else None,
        )
        return self._conn

    def _list_sources(self, with_schema=False) -> list[SourceInfo]:
        conn = self._connect()
        out, errors = self._find_sources_in_db(
            with_schema=with_schema,
            databases_override=[
                self._conn.client.project
            ],  # bigquery only allows on project per connection
        )
        return out, errors

    # caching ensures we create one bq connection per set of credentials across instances of the class
    @staticmethod
    @lru_cache()
    def _connect_helper(
        service_account_path: str | None = None,
        service_account_info_str: str | None = None,
    ) -> BaseBackend:
        from google.oauth2 import service_account

        if service_account_path is not None:
            credentials = service_account.Credentials.from_service_account_file(
                service_account_path
            )
        elif service_account_info_str is not None:
            if isinstance(service_account_info_str, str):
                service_account_info = json.loads(service_account_info_str)
            credentials = service_account.Credentials.from_service_account_info(
                service_account_info
            )
        else:
            credentials = None
        conn = ibis.bigquery.connect(credentials=credentials)

        # fixes BQ-specific error related to caching
        if not hasattr(conn, "_session_dataset") and isinstance(
            conn, ibis.backends.bigquery.Backend
        ):
            conn._session_dataset = None

        return conn

    def sql_to_df(self, query: str, limit: int | None = _QUERY_LIMIT) -> pd.DataFrame:
        conn = self._connect()
        query = self._sql_to_df_query_helper(query, limit)
        rows = conn.client.query_and_wait(query)
        if rows.total_rows < self._BQ_ITERATOR_ROW_CUTOFF:
            # faster to use iterators for small datasets
            data = [dict(row) for row in rows]
            columns = [field.name for field in rows.schema]
            df = pd.DataFrame(data, columns=columns)
        else:
            # faster to download directly for large datasets
            df = rows.to_dataframe()

        return df

    def validate_sql(self, query: str) -> ValidationOutput:
        from google.cloud.bigquery import QueryJobConfig

        conn = self._connect()

        job_config = QueryJobConfig(dry_run=True, use_query_cache=False)
        try:
            query_job = conn.client.query(query, job_config=job_config)
            bytes_processed = query_job.total_bytes_processed
            cost = bytes_processed * 5 * 1e-12  # relatively accurate for BigQuery
            return ValidationOutput(
                errors=None, bytes_processed=bytes_processed, cost=cost
            )
        except Exception as e:
            msg = str(e).split("\n\n")[0].split("prettyPrint=false: ")[-1]
            error_parsed = VinylError(
                "NA", VinylErrorType.DATABASE_ERROR, msg, dialect=self._get_name()
            )
            return ValidationOutput(
                errors=[error_parsed], bytes_processed=None, cost=None
            )


class PostgresConnector(_DatabaseConnector):
    _excluded_schemas = [
        "information_schema",
        "pg_catalog",
        "pgsodium",
        "auth",
        "extensions",
        "net",
    ]
    _allows_multiple_databases: bool = False
    _host: str
    _port: int
    _user: str
    _password: str
    _database: str

    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        tables: list[str],
    ):
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._tables = tables

        # postgres requires connecting at the database level
        dbs = set([t.split(".")[0] for t in tables])
        if len(dbs) > 1 or "*" in dbs:
            raise ValueError("Postgres connector only supports one database at a time")
        self._database = dbs.pop()

    def _connect(self) -> BaseBackend:
        self._conn = self._connect_helper(
            self._host, self._port, self._user, self._password, self._database
        )
        return self._conn

    def _list_sources(self, with_schema=False) -> list[SourceInfo]:
        self._connect()
        out, errors = self._find_sources_in_db(with_schema=with_schema)
        return out, errors

    # caching ensures we create one bq connection per set of credentials across instances of the class
    @staticmethod
    @lru_cache()
    def _connect_helper(
        host: str, port: int, user: str, password: str, database: str
    ) -> BaseBackend:
        return ibis.postgres.connect(
            host=host, port=port, user=user, password=password, database=database
        )


class RedshiftConnector(PostgresConnector):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def sql_to_df(self, query: str, limit: int | None = _QUERY_LIMIT) -> pd.DataFrame:
        conn = self._connect()
        query = self._sql_to_df_query_helper(query, limit)
        # conn.sql doesn't work for redshift, using a workaround for now while wait for issue resoluation
        # issue link here: https://ibis-project.zulipchat.com/#narrow/stream/431387-postgres/topic/Bug.20with.20conn.2Esql.28.29.20for.20Reshift
        with closing(conn.raw_sql(query)) as cursor:
            rows = cursor.fetchall()
            col_names = [desc[0] for desc in cursor.description]
            df = pd.DataFrame(rows, columns=col_names)
        return df


class SnowflakeConnector(_DatabaseConnector):
    _account: str
    _user: str
    _password: str
    _warehouse: str | None

    def __init__(
        self,
        account: str,
        user: str,
        password: str,
        tables: list[str],
        warehouse: str | None = None,
    ):
        self._account = account
        self._user = user
        self._password = password
        self._warehouse = warehouse
        self._tables = tables

    def _connect(self) -> BaseBackend:
        self._conn = self._connect_helper(
            self._account, self._user, self._password, self._warehouse
        )
        return self._conn

    def _list_sources(self, with_schema=False) -> list[SourceInfo]:
        self._connect()
        out, errors = self._find_sources_in_db(with_schema=with_schema)
        return out, errors

    # caching ensures we create one bq connection per set of credentials across instances of the class
    @staticmethod
    @lru_cache()
    def _connect_helper(
        account: str, user: str, password: str, warehouse: str | None
    ) -> BaseBackend:
        if warehouse is not None:
            return ibis.snowflake.connect(
                account=account, user=user, password=password, warehouse=warehouse
            )
        else:
            return ibis.snowflake.connect(account=account, user=user, password=password)

    def validate_sql(self, query: str) -> ValidationOutput:
        conn = self._connect()
        query = f"EXPLAIN USING JSON ({query})"
        try:
            cursor = conn.sql(query)
            out = json.loads(cursor.fetchall()[0][0])
            bytes_processed = out["GlobalStats"]["bytesAssigned"]
            cost = (
                bytes_processed * 5 * 1e-12
            )  # guess based on BQ pricing, need to update
            return ValidationOutput(
                errors=None, bytes_processed=bytes_processed, cost=cost
            )
        except Exception as e:
            error = VinylError(
                "NA",
                VinylErrorType.DATABASE_ERROR,
                str(e).split(": ", 1)[-1],
                dialect=self._get_name(),
            )
            return ValidationOutput(errors=[error], bytes_processed=None, cost=None)


class DatabricksConnector(_DatabaseConnector):
    _host: str
    _token: str
    _http_path: str

    def __init__(
        self,
        host: str,
        token: str,
        http_path: str,
        tables: list[str],
        cluster_id: str | None = None,
    ):
        self._host = host
        self._token = token
        self._http_path = http_path
        self._cluster_id = cluster_id
        self._tables = tables

    def _connect(self, use_spark: bool = True) -> BaseBackend:
        self._conn = self._connect_helper(
            self._host,
            self._token,
            self._cluster_id,
            self._http_path,
            use_spark=use_spark,
        )
        return self._conn

    def _list_sources(self, with_schema=False) -> list[SourceInfo]:
        raise NotImplementedError(
            "Databricks ibis connection not currently supported, only SQL connection."
        )

    # caching ensures we create one bq connection per set of credentials across instances of the class
    @staticmethod
    @lru_cache()
    def _connect_helper(
        host: str,
        token: str,
        cluster_id: str | None,
        http_path: str,
        use_spark: bool = True,
    ) -> BaseBackend:
        if use_spark:
            raise NotImplementedError(
                "Databricks Spark connection not yet supported. Please use Databricks SQL connection."
            )
        else:
            from databricks import sql

            return sql.connect(
                server_hostname=host, http_path=http_path, access_token=token
            )

    def sql_to_df(self, query: str, limit: int | None = _QUERY_LIMIT) -> pd.DataFrame:
        conn = self._connect(use_spark=False)
        query = self._sql_to_df_query_helper(query, limit)
        with conn.cursor() as cursor:
            cursor.execute(query)
            out = cursor.fetchall_arrow().to_pandas()
        conn.close()
        return out


@dataclass(frozen=True)
class DBTArgs:
    profiles_dir: str
    project_dir: str
    profile: Optional[str] = None
    target: Optional[str] = None
    vars: dict[str, Any] = field(default_factory=dict)
    threads: Optional[int] = None

    def to_namespace(self) -> Namespace:
        self_as_dict = asdict(self)
        return Namespace(**self_as_dict)


class DBTConnectorFull:
    def __init__(
        self,
        dbt_project_dir: str,
        dialect: DBTDialect,
        version: DBTVersion,
        dbt_profiles_dir: str | None = None,
        tables: list[str] = [],
    ):
        """
        For dbt_profiles_dir, please provide the folder (e.g. "~/.dbt"), not the file (e.g. `~/.dbt/profiles.yml`)
        """
        self.dbt_project_dir = dbt_project_dir
        self.dialect = dialect
        self.version = version
        self.tables = tables

    def __new__(
        cls,
        dbt_project_dir: str,
        dialect: DBTDialect,
        version: DBTVersion,
        dbt_profiles_dir: str | None = None,
        tables: list[str] = ["*.*.*"],
    ):
        credentials = cls._get_dbt_credentials(
            dbt_project_dir, dialect, version, dbt_profiles_dir=dbt_profiles_dir
        )
        credentials_type = type(credentials).__name__
        # if tables == []:
        #     tables = [f"{credentials.database}.{credentials.schema}.*"]
        if credentials_type == "BigQueryCredentials":
            if str(credentials.method) == "service-account":
                return BigQueryConnector(
                    service_account_path=credentials.keyfile, tables=tables
                )
            elif str(credentials.method == "service-account-json"):
                return BigQueryConnector(
                    service_account_info=credentials.keyfile_json, tables=tables
                )
            else:
                # using oauth
                return BigQueryConnector(tables=tables)
        elif credentials_type == "SnowflakeCredentials":
            pass

        elif credentials_type == "PostgresCredentials":
            return PostgresConnector(
                host=credentials.host,
                port=credentials.port,
                user=credentials.user,
                password=credentials.password,
                tables=tables,
            )

        elif credentials_type == "DuckDBCredentials":
            return DatabaseFileConnector(path=credentials.path, tables=tables)

        else:
            raise ValueError(
                f"Dialect {credentials_type.split('Credentials')[0]} is not supported"
            )

    @lru_cache()
    @staticmethod
    def _get_dbt_credentials(
        dbt_project_dir: str,
        dialect: DBTDialect,
        version: DBTVersion,
        dbt_profiles_dir: str,
    ):
        dbtproj = DBTProject(
            dbt_project_dir, dialect, version, dbt_profiles_dir=dbt_profiles_dir
        )
        credentials = dbtproj.get_profile_credentials(via_dbt=False)
        return credentials


class DBTConnectorLite:
    def __init__(
        self,
        dialect: DBTDialect,
        profile_contents: dict[str, Any],
        tables: list[str] = ["*.*.*"],
    ):
        self.dialect = dialect
        self.profile_contents = profile_contents
        self.tables = tables

    def __new__(
        cls,
        dialect: DBTDialect,
        profile_contents: dict[str, Any],
        tables: list[str] = ["*.*.*"],
    ):
        target = profile_contents["target"]
        output = profile_contents["outputs"][target]
        if dialect == DBTDialect.BIGQUERY:
            if output["method"] == "service-account-json":
                return BigQueryConnector(
                    service_account_info=output["keyfile_json"], tables=tables
                )
            elif output["method"] == "service-account":
                return BigQueryConnector(
                    service_account_path=output["keyfile"], tables=tables
                )
        elif dialect == DBTDialect.SNOWFLAKE:
            return SnowflakeConnector(
                account=output["account"],
                user=output["user"],
                password=output["password"],
                warehouse=output.get("warehouse", None),
                tables=tables,
            )
        else:
            raise ValueError(f"Dialect {dialect} is not supported")
