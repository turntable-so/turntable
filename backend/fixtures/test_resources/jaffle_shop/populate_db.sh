#!/bin/sh

# prepare dbt
dbtx deps


# populate seeds if they do not exist
DBT_CHECK=$(dbtx show --inline "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'dbt_sl_test' AND table_name = 'raw_orders')")
LAST_LINE=$(echo "$DBT_CHECK" | tail -n 1)

# run dbt seed if seeds do not exist
if echo "$LAST_LINE" | grep -q "|   True |"; then
    echo "Seeds exist, skipping populating..."
else
    echo "Seeds do not exist, populating..."
    dbtx seed --target dbt_sl_test
fi

# populate tables if they do not exist
for SCHEMA in "dev" "dbt_sl_test"; do
    DBT_CHECK=$(dbtx show --inline "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = '$SCHEMA' AND table_name = 'orders')")
    LAST_LINE=$(echo "$DBT_CHECK" | tail -n 1)

    # run dbt run if tables do not exist
    if echo "$LAST_LINE" | grep -q "|   True |"; then
        echo "$SCHEMA tables exist, skipping populating"
    else
        echo "$SCHEMA tables do not exist, populating..."
        dbtx run --target $SCHEMA
    fi
done

exec "$@"