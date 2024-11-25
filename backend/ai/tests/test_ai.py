from ai.documentation.dbt import get_column_completion, get_table_completion
from ai.embeddings import embed
from app.models import DBTCoreDetails


def test_embed():
    assert embed("text-embedding-3-small", ["hello"]) != []


def test_table_description(local_postgres):
    dbt_core_resource = DBTCoreDetails.objects.filter(resource=local_postgres).first()
    with dbt_core_resource.dbt_repo_context() as (dbtproj, dbt_path, _):
        x = get_table_completion(
            dbtproj,
            "model.jaffle_shop.customers",
            ai_model_name="openai/gpt-4o-mini",
        )
    assert x != None
    assert x != []


def test_column_description(local_postgres):
    dbt_core_resource = DBTCoreDetails.objects.filter(resource=local_postgres).first()
    with dbt_core_resource.dbt_repo_context() as (dbtproj, dbt_path, _):
        x = get_column_completion(
            dbtproj,
            {"model.jaffle_shop.customers": ["count_lifetime_orders"]},
            ai_model_name="openai/gpt-4o-mini",
        )
    assert x != None
    assert x != []
