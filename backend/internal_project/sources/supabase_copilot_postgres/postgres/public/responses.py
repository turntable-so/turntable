# type: ignore
from vinyl import Field, source  # noqa F401
from vinyl import types as t  # noqa F401

from internal_project.resources import supabase_copilot_postgres  # noqa F401


@source(resource=supabase_copilot_postgres)
class Responses:
    _table = "responses"
    _unique_name = "supabase_copilot_postgres.postgres.public.Responses"
    _schema = "public"
    _database = "postgres"
    _twin_path = "data/postgres/public/supabase_copilot_postgres.duckdb"
    _col_replace = {}

    id: t.UUID(nullable=False)
    created_at: t.Timestamp(timezone="UTC", scale=6, nullable=True)
    inference_id: t.UUID(nullable=True)
    top_choice_text: t.String(nullable=True)
    usage_details: t.JSON(nullable=True)
    quality: t.String(nullable=True)
