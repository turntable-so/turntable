from install.dbt_versions import get_pypi_all_dbt_package_versions, install_versions

versions = get_pypi_all_dbt_package_versions()
install_versions(versions)
