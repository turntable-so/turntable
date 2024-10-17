import os

from django.core.management.base import BaseCommand
from app.models import Asset
import re

SYSTEM_PROMPT = """
You are an expert data analyst and data engineer who is a world expert at dbt (data build tool.
You have mastery in writing sql, jinja, dbt macros and architecturing data pipelines using marts, star schema architecures and designs for efficient and effective analytics data pipelines.
You will be provided with dbt project context that includes:
1. The data lineage
2. table schemas 
3. file contents

Rules:
- Be as helpful as possible and answer all questions to the best of your ability.
- Please reference the latest dbt documentation at docs.getdbt.com if needed
- You may reference parts of the cntext that was pa
- You will only respond in markdown, using headers, paragraph, bulleted lists and sql/dbt code blocks if needed for the best answer quality possible
- IMPORTANT: make sure all generate sql, dbt jinja examples or included code blocks are syntactically correct and will run on the target database postgres
"""

links = [
    {
        "id": "urn:li:dataset:(urn:li:dataPlatform:postgres,mydb.dbt_sl_test.stg_customers,PROD)_urn:li:dataset:(urn:li:dataPlatform:postgres,mydb.dbt_sl_test.customers,PROD)",
        "source_id": "urn:li:dataset:(urn:li:dataPlatform:postgres,mydb.dbt_sl_test.stg_customers,PROD)",
        "target_id": "urn:li:dataset:(urn:li:dataPlatform:postgres,mydb.dbt_sl_test.customers,PROD)",
    },
    {
        "id": "urn:li:dataset:(urn:li:dataPlatform:postgres,mydb.dbt_sl_test.order_items,PROD)_urn:li:dataset:(urn:li:dataPlatform:postgres,mydb.dbt_sl_test.customers,PROD)",
        "source_id": "urn:li:dataset:(urn:li:dataPlatform:postgres,mydb.dbt_sl_test.order_items,PROD)",
        "target_id": "urn:li:dataset:(urn:li:dataPlatform:postgres,mydb.dbt_sl_test.customers,PROD)",
    },
    {
        "id": "urn:li:dataset:(urn:li:dataPlatform:postgres,mydb.dbt_sl_test.order_items,PROD)_urn:li:dataset:(urn:li:dataPlatform:postgres,mydb.dbt_sl_test.orders,PROD)",
        "source_id": "urn:li:dataset:(urn:li:dataPlatform:postgres,mydb.dbt_sl_test.order_items,PROD)",
        "target_id": "urn:li:dataset:(urn:li:dataPlatform:postgres,mydb.dbt_sl_test.orders,PROD)",
    },
    {
        "id": "urn:li:dataset:(urn:li:dataPlatform:postgres,mydb.dbt_sl_test.orders,PROD)_urn:li:dataset:(urn:li:dataPlatform:postgres,mydb.dbt_sl_test.customers,PROD)",
        "source_id": "urn:li:dataset:(urn:li:dataPlatform:postgres,mydb.dbt_sl_test.orders,PROD)",
        "target_id": "urn:li:dataset:(urn:li:dataPlatform:postgres,mydb.dbt_sl_test.customers,PROD)",
    },
]

current_file = """
with

customers as (

    select * from {{ ref('stg_customers') }}

),

orders_table as (

    select * from {{ ref('orders') }}

),

order_items_table as (

    select * from {{ ref('order_items') }}
),

order_summary as (

    select
        customer_id,

        count(distinct orders.order_id) as count_lifetime_orders,
        count(distinct orders.order_id) > 1 as is_repeat_buyer,
        min(orders.ordered_at) as first_ordered_at,
        max(orders.ordered_at) as last_ordered_at,
        sum(order_items.product_price) as lifetime_spend_pretax,
        sum(orders.order_total) as lifetime_spend

    from orders_table as orders
    
    left join order_items_table as order_items on orders.order_id = order_items.order_id
    
    group by 1

),

joined as (

    select
        customers.*,
        order_summary.count_lifetime_orders,
        order_summary.first_ordered_at,
        order_summary.last_ordered_at,
        order_summary.lifetime_spend_pretax,
        order_summary.lifetime_spend,

        case
            when order_summary.is_repeat_buyer then 'returning'
            else 'new'
        end as customer_type

    from customers

    left join order_summary
        on customers.customer_id = order_summary.customer_id

)

select * from joined
"""

related_assets = [
    "0:urn:li:dataset:(urn:li:dataPlatform:postgres,mydb.dbt_sl_test.orders,PROD)",
    "0:urn:li:dataset:(urn:li:dataPlatform:postgres,mydb.dbt_sl_test.order_items,PROD)",
    "0:urn:li:dataset:(urn:li:dataPlatform:postgres,mydb.dbt_sl_test.customers,PROD)",
    "0:urn:li:dataset:(urn:li:dataPlatform:postgres,mydb.dbt_sl_test.stg_customers,PROD)",
]


def asset_md(asset: Asset, contents: str):
    columns = asset.columns.all()
    column_table = (
        "| Name | Type | Description |\n|-------------|-----------|-------------|\n"
    )
    for column in columns:
        column_table += (
            f"| {column.name} | {column.type} | {column.description or ''} |\n"
        )

    description = asset.description or "No description available"
    return f"""
## {asset.name}
{description}

## Schema
{column_table}

## Contents
```sql
{contents}
```
"""


def extract_model_name(urn_string):
    pattern = r",[^,]+\.([^,]+),[^)]+\)$"
    match = re.search(pattern, urn_string)
    if match:
        return match.group(1)
    return None


def lineage_ascii(edges):
    # Build the graph
    graph = {}
    all_nodes = set()
    for edge in edges:
        source, target = edge["source"], edge["target"]
        if source not in graph:
            graph[source] = set()
        graph[source].add(target)
        all_nodes.add(source)
        all_nodes.add(target)

    # Find root nodes (nodes with no incoming edges)
    root_nodes = all_nodes - set().union(*graph.values())

    def print_node(node, prefix="", is_last=True):
        result = prefix
        result += "└── " if is_last else "├── "
        result += f"{node}\n"

        if node in graph:
            children = sorted(graph[node])
            for i, child in enumerate(children):
                next_prefix = prefix + ("    " if is_last else "│   ")
                result += print_node(child, next_prefix, i == len(children) - 1)

        return result

    ascii_graph = "```\n"
    for i, root in enumerate(sorted(root_nodes)):
        ascii_graph += print_node(root, "", i == len(root_nodes) - 1)
    ascii_graph += "```"

    return ascii_graph


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        # map each id to a schema (with name, type and description)
        assets = Asset.objects.filter(id__in=related_assets)

        instructions = "add a customer vip model that ranks users by lifetime sales"

        dbt_details = assets[0].resource.dbtresource_set.first()
        with dbt_details.dbt_transition_context() as (
            transition,
            _,
            repo,
        ):
            transition.mount_manifest(defer=True)
            asset_mds = []
            # schemas
            for asset in assets:
                # find each file for the related assets
                with open(
                    os.path.join(
                        repo.working_tree_dir,
                        "models",
                        transition.after.manifest.get("nodes")
                        .get(asset.unique_name.lower())
                        .get("path"),
                    )
                ) as file:
                    contents = file.read()
                    asset_mds.append(asset_md(asset, contents))

            # lineage information
            edges = []
            for link in links:
                source_model = extract_model_name(link["source_id"])
                target_model = extract_model_name(link["target_id"])
                edges.append({"source": source_model, "target": target_model})

            lineage_md = f"""
# Model lineage
IMPORTANT: keep in mind how these are connected to each other. You may need to add or modify this structure to complete a task.
{lineage_ascii(edges)}
"""
            assets = "\n".join(asset_mds)
            # file contents
            output = f"""{lineage_md}
{assets}
User Instructions: {instructions}
"""
            print(output)
