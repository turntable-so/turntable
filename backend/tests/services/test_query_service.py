import pytest
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
import ibis

from app.models.resources import PostgresDetails, ResourceType, ResourceSubtype
from app.models import Resource, User, Workspace

User = get_user_model()


def get_postgres_metadata(connection):
    cursor = connection.cursor()

    # Get schemas
    cursor.execute(
        """
        SELECT schema_name 
        FROM information_schema.schemata 
        WHERE schema_name NOT IN ('information_schema', 'pg_catalog')
    """
    )
    schemas = [row[0] for row in cursor.fetchall()]

    metadata = {}
    for schema in schemas:
        # Get tables for each schema
        cursor.execute(
            f"""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = %s AND table_type = 'BASE TABLE'
        """,
            (schema,),
        )
        tables = [row[0] for row in cursor.fetchall()]

        metadata[schema] = {}
        for table in tables:
            # Get columns for each table
            cursor.execute(
                f"""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_schema = %s AND table_name = %s
            """,
                (schema, table),
            )
            columns = [(row[0], row[1]) for row in cursor.fetchall()]

            metadata[schema][table] = columns

    return metadata


@pytest.mark.django_db
def test_query_postgres_resource(local_postgres):
    connection = ibis.postgres.connect(
        host=local_postgres.details.host,
        port=local_postgres.details.port,
        user=local_postgres.details.username,
        password=local_postgres.details.password,
        database=local_postgres.details.database,
    )
    query = """
        SELECT * FROM mydb.dbt_sl_test.stg_customers
    """

    table = connection.sql(query)
    df = table.execute()
    breakpoint()
