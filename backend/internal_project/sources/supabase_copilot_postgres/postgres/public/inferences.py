# type: ignore
from vinyl import Field, source  # noqa F401
from vinyl import types as t  # noqa F401

from internal_project.resources import supabase_copilot_postgres  # noqa F401


@source(resource=supabase_copilot_postgres)
class Inferences:
    _table = "inferences"
    _unique_name = "supabase_copilot_postgres.postgres.public.Inferences"
    _schema = "public"
    _database = "postgres"
    _twin_path = "data/postgres/public/supabase_copilot_postgres.duckdb"
    _col_replace = {}

    id: t.UUID(nullable=False)
    created_at: t.Timestamp(timezone="UTC", scale=6, nullable=True)
    input_text: t.String(nullable=True)
    prompt_text: t.String(nullable=True)
    open_ai_prompt_text: t.String(nullable=True)
    model_config: t.JSON(nullable=True)
    prompt_type: t.String(nullable=True)
