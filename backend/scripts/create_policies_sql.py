import os
from urllib.parse import urlparse

from dotenv import load_dotenv

load_dotenv()


def get_postgres_user():
    url = os.getenv("SUPABASE_URL")
    parsed_url = urlparse(url)
    account = parsed_url.hostname.split(".")[0]
    return f"postgres.{account}"


def get_policy_sql(
    domain: str,
    table: str,
    policy_name: str,
    policy_type: str,
    column: str,
    column_is_adjusted: bool = False,
    indexes: bool = True,
):
    policy_sql = ""
    if indexes:
        adj_column_name = "".join(c if c.isalnum() else "_" for c in column)
        index_name = f"{table}_{adj_column_name}_idx"
        policy_sql += f"drop index if exists {index_name};\n\n"
        if column_is_adjusted:
            index_clause_helper = f"({column})"
        else:
            index_clause_helper = column
        policy_sql += f"create index {index_name} on {domain}.{table} using btree ({index_clause_helper});\n\n"
    full_policy_name = f"{policy_name}_{domain}_{table}_{policy_type.lower()}"
    policy_sql += f"drop policy if exists {full_policy_name} on {domain}.{table};\n\n"
    policy_check_helper = (
        "( SELECT ((auth.jwt() -> 'app_metadata'::text) ->> 'tenant_id'::text))"
    )
    policy_check = f"({column} = {policy_check_helper})"
    policy_sql += f"create policy {full_policy_name}\n"
    policy_sql += f"on {domain}.{table}\n"
    policy_sql += "as RESTRICTIVE\n"
    policy_sql += f"for {policy_type}\n"
    policy_sql += "to authenticated\n"
    if policy_type != "INSERT":
        policy_sql += f"using ({policy_check})"
    if policy_type == "UPDATE":
        policy_sql += "\n"
    if policy_type in ["INSERT", "UPDATE"]:
        policy_sql += f"with check ({policy_check})"
    policy_sql += ";\n"

    return policy_sql


if __name__ == "__main__":
    tables = [
        "assets",
        "asset_links",
        "blocks",
        "block_links",
        "columns",
        "column_links",
        "github_installations",
        "models",
        "notebook_blocks",
        "notebooks",
        "profiles",
        "repositories",
        "resources",
    ]
    policy_types = ["SELECT", "INSERT", "UPDATE"]
    out_sql = ""
    # Define your SQL query
    for i, type in enumerate(policy_types):
        # create core policies
        for table in tables:
            policy_sql = get_policy_sql(
                "public", table, "tenant", type, "tenant_id", indexes=i == 0
            )
            out_sql += policy_sql + "\n"

        # create storage policies
        policy_sql = get_policy_sql(
            "storage",
            "objects",
            "tenant",
            type,
            "path_tokens[2]",
            indexes=i == 0,
            column_is_adjusted=True,
        )
        out_sql += policy_sql + "\n"

    print(out_sql)
