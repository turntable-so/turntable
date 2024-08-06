import pytest

from ai.documentation.dbt import get_column_completion, get_table_completion
from ai.embeddings import embed


def test_embed():
    assert embed("text-embedding-3-small", ["hello"]) != []


@pytest.mark.django_db
def test_table_description(test_dbt_project):
    x = get_table_completion(
        test_dbt_project,
        "model.jaffle_shop.customers",
        ai_model_name="gpt-4o",
    )
    assert x != None
    assert x != []


@pytest.mark.django_db
def test_column_description(test_dbt_project):
    x = get_column_completion(
        test_dbt_project,
        {"model.jaffle_shop.customers": ["count_lifetime_orders"]},
        ai_model_name="gpt-4o",
    )
    assert x != None
    assert x != []
