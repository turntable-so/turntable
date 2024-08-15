import re
from urllib.parse import urlparse


def parse_urn(urn):
    # Use regular expressions to extract the main URN and the nested URN
    pattern = r"^(urn:[^:]+:[^:]+):\((urn:[^:]+:[^:]+:[^:]+),([^,]+),([^)]+)\)$"
    match = re.match(pattern, urn)

    if not match:
        raise ValueError("Invalid URN format")

    main_urn = match.group(1)
    nested_urn = match.group(2)
    identifier = match.group(3)
    environment = match.group(4)

    return {
        "main_urn": main_urn,
        "nested_urn": parse_nested_urn(nested_urn),
        "identifier": identifier,
        "environment": environment,
    }


def parse_nested_urn(urn):
    # Parse the nested URN
    parsed_urn = urlparse(urn)

    scheme = parsed_urn.scheme
    namespace = parsed_urn.netloc
    entity_type = parsed_urn.path.split(":")[0]
    entity_name = parsed_urn.path.split(":")[1]

    return {
        "scheme": scheme,
        "namespace": namespace,
        "entity_type": entity_type,
        "entity_name": entity_name,
    }


# Example URN with nested URN
urn = "urn:li:dataset:(urn:li:dataPlatform:bigquery,capchase.analytics.parameters,PROD)"

parsed_urn = parse_urn(urn)

print(parsed_urn)
