import datetime as dt
from typing import Any


def get_open_lineage_name(networkx_field: str):
    split_ = networkx_field.split(".")
    if networkx_field.startswith("source"):
        namespace = ".".join(split_[:2])
        name = ".".join(split_[2:3])
        field = ".".join(split_[4:])
    else:
        namespace = ".".join(split_[:2])
        name = split_[2]
        field = ".".join(split_[3:])
    return namespace, name, field


def turntablecli_to_openlineage(current_output: Any):
    """
    This function converts the lineage data from TurntableCLI to OpenLineage format in alignment with the [Column Level Lineage Dataset Facet](https://openlineage.io/docs/spec/facets/dataset-facets/column_lineage_facet/).

    Some differences:
        - We add the "how" field to the inputFields in the ColumnLineageDatasetFacet. This specified more information on the connection between the fields.
        - The specific naming of each column may be different from how dbt handles table lineage. This can be easily changed by modifying the `get_open_lineage_name` function above.

    Things that will have to be handled elsewhere:
        - How to show errors (the third item of the current output)
    """

    event_dict = {}
    for link in current_output["stdout"]["lineage"]["links"]:
        try:
            source_namespace, source_name, source_field = get_open_lineage_name(
                link["source"]
            )
            target_namespace, target_name, target_field = get_open_lineage_name(
                link["target"]
            )
        except Exception as e:
            # rarely, there can be field naming issues. One large project has 0.2%. Just printing for now, but you can also add to errors if you want.
            print(e)
            continue

        if (source_namespace, source_name) not in event_dict:
            event_dict[(source_namespace, source_name)] = {
                "event_time": str(dt.datetime.now()),
                "inputs": [
                    {
                        "namespace": source_namespace,
                        "name": source_name,
                    }
                ],
                "outputs": [],
            }
        found = False
        field_dict = {
            "namespace": source_namespace,
            "name": source_name,
            "field": source_field,
            "how": link["ntype"],
        }
        for out in event_dict[(source_namespace, source_name)]["outputs"]:
            if out["namespace"] == target_namespace and out["name"] == target_name:
                found = True

                if target_field not in out["facets"]["columnLineage"]["fields"]:
                    out["facets"]["columnLineage"]["fields"][target_field] = {
                        "inputFields": [field_dict]
                    }
                else:
                    out["facets"]["columnLineage"]["fields"][target_field][
                        "inputFields"
                    ].append(field_dict)
        if found is False:
            event_dict[(source_namespace, source_name)]["outputs"].append(
                {
                    "namespace": target_namespace,
                    "name": target_name,
                    "facets": {
                        "columnLineage": {
                            "_producer": "NA",
                            "_schemaURL": "https://openlineage.io/spec/facets/1-0-1/ColumnLineageDatasetFacet.json",
                            "fields": {target_field: {"inputFields": [field_dict]}},
                        }
                    },
                }
            )
    out = []
    for i, val in enumerate(event_dict.values()):
        if i == 0:
            val["eventType"] = "START"
        elif i == len(event_dict) - 1:
            val["eventType"] = "COMPLETE"
        else:
            val["eventType"] = "RUNNING"
        out.append(val)

    return out
