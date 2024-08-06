# helper used within dbt internals
import json
from abc import ABC
from enum import Enum

from vinyl.lib.dbt_methods import DBTVersion
from vinyl.lib.utils.text import decrypt_secret

from app.models import Resource

DEFAULT_THREADS = 4


class DBTDialectBase(ABC):
    def get_dbt_credentials_dataclass_name(self):
        raise NotImplementedError

    def dbt_profile_contents_helper(self, resource: Resource, profile):
        raise NotImplementedError


class DBTDialectBigQuery(DBTDialectBase):
    def get_dbt_credentials_dataclass_name(self):
        return "BigQueryCredentials"

    def dbt_profile_contents_helper(self, resource: Resource, profile):
        profile_output = profile["outputs"]["prod"]
        config = resource.config
        profile["outputs"]["prod"]["project"] = resource.config["project"]

        if "dataset" in config:
            profile_output["schema"] = config["dataset"]
        elif "schema" in config:
            profile_output["schema"] = config["schema"]

        profile_output["threads"] = int(config.get("threads", DEFAULT_THREADS))
        decrypted = json.loads(decrypt_secret(resource.profile.encrypted_secret))
        if decrypted.get("type", None) == "service_account":
            profile_output["method"] = "service-account-json"
            profile_output["keyfile_json"] = decrypted
        else:
            raise ValueError("Only service account profiles are supported currently")

        return profile


class DBTDialectSnowflake(DBTDialectBase):
    def get_dbt_credentials_dataclass_name(self):
        return "SnowflakeCredentials"

    def dbt_profile_contents_helper(self, resource: Resource, profile):
        profile_output = profile["outputs"]["prod"]
        config = resource.config

        # requirements
        profile_output["schema"] = config["schema"]
        profile_output["account"] = config["account"]
        profile_output["user"] = config["user"]
        profile_output["password"] = decrypt_secret(resource.profile.encrypted_secret)
        profile_output["database"] = config["database"]

        # optional
        if "warehouse" in config:
            profile_output["warehouse"] = config["warehouse"]
        if "role" in config:
            profile_output["role"] = config["role"]

        profile_output["threads"] = int(config.get("threads", DEFAULT_THREADS))
        return profile


class DBTDialectPostgres(DBTDialectBase):
    def get_dbt_credentials_dataclass_name(self):
        return "PostgresCredentials"


class DBTDialectDuckDB(DBTDialectBase):
    def get_dbt_credentials_dataclass_name(self):
        return "DuckDBCredentials"


class DBTDialect(Enum):
    BIGQUERY = "bigquery"
    SNOWFLAKE = "snowflake"
    POSTGRES = "postgres"
    DUCKDB = "duckdb"

    @property
    def dialect_class(self):
        if self == DBTDialect.BIGQUERY:
            return DBTDialectBigQuery()
        elif self == DBTDialect.SNOWFLAKE:
            return DBTDialectSnowflake()
        elif self == DBTDialect.POSTGRES:
            return DBTDialectPostgres()
        elif self == DBTDialect.DUCKDB:
            return DBTDialectDuckDB()
        else:
            raise ValueError(f"Unsupported dialect: {self}")

    def get_dbt_credentials_dataclass_name(self):
        return self.dialect_class.get_dbt_credentials_dataclass_name()

    def get_dbt_profile_contents_from_resource(self, resource):
        profile = {}
        profile["target"] = "prod"
        profile["outputs"] = {}
        profile["outputs"]["prod"] = {}
        dialect = get_dbt_dialect_from_resource(resource)
        profile["outputs"]["prod"]["type"] = dialect.value.lower()
        return self.dialect_class.dbt_profile_contents_helper(resource, profile)


def get_dbt_dialect_from_resource(resource: Resource):
    return DBTDialect._value2member_map_[resource.config["dialect"]]


def get_dbt_version_from_resource(resource: Resource):
    version_string = resource.config["version"]
    return DBTVersion._value2member_map_[version_string]
