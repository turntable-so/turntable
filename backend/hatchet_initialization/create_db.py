import os

import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def create_hatchet_db():
    if os.getenv("STAGING") == "true":
        return {
            "success": False,
            "msg": "Skipping hatchet database creation on staging.",
        }
    elif os.getenv("LOCAL_DB") == "true":
        dbname = os.getenv("POSTGRES_DB")
        user = os.getenv("POSTGRES_USER")
        password = os.getenv("POSTGRES_PASSWORD")
        host = os.getenv("POSTGRES_HOST")
        port = os.getenv("POSTGRES_PORT")

        connection = psycopg2.connect(
            dbname=dbname, user=user, password=password, host=host, port=port
        )
    else:
        database_url = os.getenv("DATABASE_URL")
        connection = psycopg2.connect(dsn=database_url)

    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = connection.cursor()

    # Check if the database exists
    hatchet_db = os.environ.get("DATABASE_POSTGRES_DB_NAME")
    cursor.execute(
        "SELECT 1 FROM pg_database WHERE datname = %(db)s", {"db": hatchet_db}
    )
    exists = cursor.fetchone()

    if not exists:
        # Create the database
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(hatchet_db)))
        cursor.execute(
            sql.SQL("ALTER DATABASE {} OWNER to {}").format(
                sql.Identifier(hatchet_db), sql.Identifier(user)
            )
        )

        out = {"success": True, "msg": f"Database '{hatchet_db}' created successfully."}
    else:
        out = {"success": False, "msg": f"Database '{hatchet_db}' already exists."}

    cursor.close()
    connection.close()
    return out


if __name__ == "__main__":
    print(create_hatchet_db())
