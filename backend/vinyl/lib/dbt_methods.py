from argparse import Namespace
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class DBTVersion(Enum):
    V1_3 = "1.3"
    V1_4 = "1.4"
    V1_5 = "1.5"
    V1_6 = "1.6"
    V1_7 = "1.7"


class DBTDialect(Enum):
    BIGQUERY = "bigquery"
    SNOWFLAKE = "snowflake"
    POSTGRES = "postgres"
    DUCKDB = "duckdb"


class DBTError:
    RUNTIME = "Runtime Error"
    COMPILATION = "Compilation Error"
    DEPENDENCY = "Dependency Error"
    DATABASE = "Database Error"
    MISCELLANEOUS = "Error"

    @classmethod
    def has_dbt_error(cls, text):
        if cls.RUNTIME in text:
            return True
        elif cls.COMPILATION in text:
            return True
        elif cls.DEPENDENCY in text:
            return True
        elif cls.DATABASE in text:
            return True
        elif cls.MISCELLANEOUS in text:
            return True

        return False


MAX_DIALECT_VERSION = {
    DBTDialect.BIGQUERY.value: {
        DBTVersion.V1_3.value: "1.3.3",
        DBTVersion.V1_4.value: "1.4.5",
        DBTVersion.V1_5.value: "1.5.9",
        DBTVersion.V1_6.value: "1.6.12",
        DBTVersion.V1_7.value: "1.7.7",
    },
    DBTDialect.SNOWFLAKE.value: {
        DBTVersion.V1_3.value: "1.3.3",
        DBTVersion.V1_4.value: "1.4.5",
        DBTVersion.V1_5.value: "1.5.7",
        DBTVersion.V1_6.value: "1.6.8",
        DBTVersion.V1_7.value: "1.7.5",
    },
    DBTDialect.POSTGRES.value: {
        DBTVersion.V1_3.value: "1.3.7",
        DBTVersion.V1_4.value: "1.4.9",
        DBTVersion.V1_5.value: "1.5.11",
        DBTVersion.V1_6.value: "1.6.11",
        DBTVersion.V1_7.value: "1.7.11",
    },
    DBTDialect.DUCKDB.value: {
        DBTVersion.V1_3.value: "1.3.4",
        DBTVersion.V1_4.value: "1.4.2",
        DBTVersion.V1_5.value: "1.5.2",
        DBTVersion.V1_6.value: "1.6.2",
        DBTVersion.V1_7.value: "1.7.3",
    },
}


@dataclass(frozen=True)
class DBTArgs:
    profiles_dir: str
    project_dir: str
    profile: str | None = None
    target: str | None = None
    vars: str | Any = field(default_factory=dict)
    threads: int | None = None

    def to_namespace(self) -> Namespace:
        self_as_dict = asdict(self)
        return Namespace(**self_as_dict)


def get_dbt_dialect_from_resource_dict(resource_dict: dict[str, Any]):
    return DBTDialect._value2member_map_[resource_dict["config"]["dialect"]]


def get_dbt_version_from_resource_dict(resource_dict: dict[str, Any]):
    version_string = resource_dict["config"]["version"]
    return DBTVersion._value2member_map_[version_string]
