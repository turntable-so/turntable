#!/bin/sh

# prepare dbt
dbtx deps

# check if seeds exist, using one table as proxy
DBT_CHECK=$(dbtx show --inline "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'dbt_sl_test' AND table_name = 'raw_orders')")
LAST_LINE=$(echo "$DBT_CHECK" | tail -n 1)

# run dbt seed if tables do not exist
if echo "$LAST_LINE" | grep -q "|   True |"; then
    echo "Tables exist, skipping populating the database"
else
    echo "Tables do not exist, populating the database"
    dbtx seed
    dbtx run
fi

exec "$@"