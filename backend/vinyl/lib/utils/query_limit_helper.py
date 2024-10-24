from vinyl.lib.utils.query import _QUERY_LIMIT
from vinyl.lib.utils.text import _generate_random_ascii_string


def query_limit_helper(
    query: str, limit: int | None = _QUERY_LIMIT, bypass: bool = False
) -> str:
    if bypass:
        return query
    alias = _generate_random_ascii_string(8)
    query = f"select * from ({query}) as {alias}"
    if limit:
        query += f" limit {limit}"
    return query
