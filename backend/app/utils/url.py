from urllib.parse import urlencode


def build_url(base_url, params):
    if not params:
        return base_url

    # Convert the params dictionary into a query string
    query_string = urlencode(params)

    # Concatenate the base URL with the query string
    full_url = f"{base_url}?{query_string}"

    return full_url
