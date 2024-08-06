# Standard library
import json
import subprocess
from typing import List
import urllib.request
from time import sleep
import concurrent.futures as cf


# Local
import dbtenv
from dbtenv import Version

logger = dbtenv.LOGGER

DBT_ADAPTER_TYPES = [
    "bigquery",
    # 'clickhouse',
    # 'databricks',
    # 'dremio',
    # 'duckdb',
    # 'exasol',
    # 'firebolt',
    # 'materialize',
    # 'oracle',
    # 'postgres',
    # 'presto',
    # 'redshift',
    # 'rockset',
    # 'singlestore',
    "snowflake",
    # 'spark',
    # 'sqlserver',
    # 'synapse',
    # 'teradata',
    # 'trino',
    # 'vertica',
]


def get_pypi_package_metadata(package: str) -> str:
    package_json_url = f"https://pypi.org/pypi/{package}/json"
    logger.debug(f"Fetching {package} package metadata from {package_json_url}.")
    with urllib.request.urlopen(package_json_url) as package_json_response:
        return json.load(package_json_response)


def get_pypi_package_versions(adapter_type: str) -> List:
    package_metadata = get_pypi_package_metadata(f"dbt-{adapter_type}")
    possible_versions = (
        (Version(adapter_type=adapter_type, version=version), files)
        for version, files in package_metadata["releases"].items()
    )
    return [
        version
        for version, files in possible_versions
        if any(not file["yanked"] for file in files)
    ]


def get_pypi_all_dbt_package_versions() -> List:
    version_objs = []
    with cf.ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(get_pypi_package_versions, adapter_type)
            for adapter_type in DBT_ADAPTER_TYPES
        ]
        for future in cf.as_completed(futures):
            try:
                version_objs += future.result()
            except Exception as e:
                print(f"Error executing task: {e}")
    all_versions = [
        i.pip_specifier
        for i in version_objs
        if i.version[0] >= 1 and i.version[1] >= 3 and len(i.version) <= 3
    ]
    return all_versions


def get_previously_installed_versions() -> List:
    result = subprocess.Popen(
        ["dbtenv", "--quiet", "versions", "--installed"], stdout=subprocess.PIPE
    )
    output = result.communicate()[0].decode().split("\n")
    output_adj = [f"dbt{i.split('dbt')[-1].strip()}" for i in output if i]
    return output_adj


def install_version(v: str, installed: List[str]):
    if v in installed:
        print(f"Already installed {v}")
    else:
        try:
            print(f"Installing {v}...")
            subprocess.run(
                f"dbtenv install {v}",
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            print(f"Installed {v}.")
        except subprocess.CalledProcessError as e:
            print(f"Didn't install {v}, error: {e}")
            sleep(0.05)


def install_versions(versions: List[str]):
    previously_installed = get_previously_installed_versions()
    with cf.ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(install_version, v, previously_installed) for v in versions
        ]
        cf.wait(futures)
