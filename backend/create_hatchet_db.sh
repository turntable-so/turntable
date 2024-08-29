#!/bin/bash

if [ "$LOCAL_DB" = "true" ]; then
    URL="postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@$POSTGRES_HOST:$POSTGRES_PORT/$POSTGRES_DB"
    USER=$POSTGRES_USER
else
    URL=$DATABASE_URL
    USER=$(echo "$URL" | sed -n 's|^postgresql://\([^:]*\):.*$|\1|p')
fi

# create db
if psql "$URL" -lqt | cut -d \| -f 1 | grep -qw "$1"; then
    echo "Database \"$1\" already exists."
else
    psql "$URL" -c "CREATE DATABASE \"$1\""
fi

psql "$URL" -c "ALTER DATABASE \"$1\" OWNER TO \"$USER\""