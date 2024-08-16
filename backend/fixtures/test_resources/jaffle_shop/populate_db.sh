#!/bin/sh
set -e

# install dbt
pip install uv
uv pip install dbt-postgres~=1.8.0 --system

# prepare dbt
dbt deps

# check if seeds exist, using one table as proxy
DBT_CHECK=$(dbt show --inline "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'dbt_sl_test' AND table_name = 'raw_orders')")
LAST_LINE=$(echo "$DBT_CHECK" | tail -n 1)

# run dbt seed if tables do not exist
if echo "$LAST_LINE" | grep -q "|   True |"; then
    echo "Tables exist, skipping populating the database"
else
    echo "Tables do not exist, populating the database"
    dbt seed
    dbt run
fi