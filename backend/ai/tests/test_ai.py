import pytest

from ai.documentation.dbt import get_column_completion, get_table_completion
from ai.embeddings import embed
from app.models import DBTCoreDetails


def test_embed():
    assert embed("text-embedding-3-small", ["hello"]) != []


@pytest.mark.django_db
def test_table_description(local_postgres):
    dbt_core_resources = DBTCoreDetails.objects.filter(resource=local_postgres)
    with dbt_core_resources[0].dbt_repo_context() as (dbtproj, dbt_path, _):
        x = get_table_completion(
            dbtproj,
            "model.jaffle_shop.customers",
            ai_model_name="gpt-4o-mini",
        )
    assert x != None
    assert x != []


@pytest.mark.django_db
def test_column_description(local_postgres):
    dbt_core_resources = DBTCoreDetails.objects.filter(resource=local_postgres)
    with dbt_core_resources[0].dbt_repo_context() as (dbtproj, dbt_path, _):
        x = get_column_completion(
            dbtproj,
            {"model.jaffle_shop.customers": ["count_lifetime_orders"]},
            ai_model_name="gpt-4o-mini",
        )
    assert x != None
    assert x != []
