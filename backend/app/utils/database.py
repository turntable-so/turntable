from django.db.models import Model

from app.models import Resource


def delete_and_upsert(
    instances: list[Model],
    resource: Resource,
    indirect_instances: list[Model] | None = None,
):
    if resource is None or resource.id is None:
        raise ValueError(
            "Resource must have an id to use the `delete_and_upsert` function"
        )
    if len(instances) == 0:
        return
    model_types = set([type(i) for i in instances])
    if len(model_types) > 1:
        raise ValueError("All instances must be of the same model type")

    model_type = model_types.pop()
    primary_key_name = model_type._meta.pk.name
    other_field_names = [
        field.name
        for field in model_type._meta.fields
        if field.name != primary_key_name
    ]
    if not hasattr(model_type, "get_for_resource"):
        raise ValueError(
            f"Model {model_type.__name__} must have a get_for_resource method to use the `delete_and_upsert` function"
        )
    cur_instances = model_type.get_for_resource(resource.id)
    cur_instance_ids = (
        [v[primary_key_name] for v in cur_instances.values(primary_key_name).values()]
        if cur_instances.exists()
        else []
    )

    new_primary_keys = [str(getattr(i, primary_key_name)) for i in instances]

    # delete instances that are no longer in the new list
    to_delete = list(set(cur_instance_ids) - set(new_primary_keys))
    if to_delete:
        model_type.objects.filter(id__in=to_delete).delete()

    # upsert the new instances
    model_type.objects.bulk_create(
        instances,
        update_conflicts=True,
        update_fields=other_field_names,
        unique_fields=[primary_key_name],
    )

    # insert the indirect instances if they don't exist.
    ## This functionality is necessary because links can exist across resources, and if the underyling nodes are not present, the link creation will raise a FK error.
    ## That said, we don't want to add these temporary nodes if the true nodes already exist in the graph.
    if indirect_instances is not None:
        model_type.objects.bulk_create(
            indirect_instances,
            ignore_conflicts=True,
        )
