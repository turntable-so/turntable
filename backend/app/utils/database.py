import pgbulk
from django.db.models import Model
from django.utils import timezone

from app.models import Resource


def get_pg_instance_ids(model_type: Model, resource: Resource):
    ## This function is used to get the primary keys of instances of a model that are associated with a resource.
    ## Some instances are associated with multiple resources, `inclusive` includes these where `exclusive`` excludes these.
    out = []
    if not hasattr(model_type, "get_for_resource"):
        raise ValueError(
            f"Model {model_type.__name__} must have a get_for_resource method to use the `delete_and_upsert` function"
        )
    instances_ls = (
        model_type.get_for_resource(resource.id),
        model_type.get_for_resource(resource.id, inclusive=False),
    )
    pk_name = model_type._meta.pk.name
    for instances in instances_ls:
        if instances.exists():
            out_it = [str(v) for v in instances.values_list(pk_name, flat=True)]
        else:
            out_it = []
        out.append(out_it)
    return out


def pg_delete_and_upsert(
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
    pk_name = model_type._meta.pk.name
    cur_ids_inclusive, cur_ids_exclusive = get_pg_instance_ids(model_type, resource)
    new_primary_keys = [str(getattr(i, pk_name)) for i in instances]

    # delete instances that are no longer in the new list
    to_delete = list(set(cur_ids_exclusive) - set(new_primary_keys))
    base_delete = model_type.objects.filter(id__in=to_delete)
    model_field_names = [f.name for f in model_type._meta.get_fields()]
    if "is_indirect" in model_field_names:
        # only delete direct instances for now, indirect deletion handled later. This is required to ensure cross-resource connections are maintained.
        base_delete = base_delete.filter(is_indirect=False)
    base_delete.delete()

    # upsert the new instances
    new_instances = []
    update_instances = []
    for i in instances:
        if str(i.id) not in cur_ids_inclusive:
            new_instances.append(i)
        else:
            i.updated_at = timezone.now()
            update_instances.append(i)
    pgbulk.copy(
        model_type,
        new_instances,
    )
    pgbulk.update(
        model_type,
        update_instances,
        ignore_unchanged=True,
    )

    # insert the indirect instances if they don't exist.
    ## This functionality is necessary because links can exist across resources, and if the underyling nodes are not present, the link creation will raise a FK error.
    ## That said, we don't want to add these temporary nodes if the true nodes already exist in the graph.
    if indirect_instances is not None:
        cur_ids = [
            str(id) for id in model_type.objects.all().values_list(pk_name, flat=True)
        ]
        new_indirect_instances = [
            i for i in indirect_instances if str(i.id) not in cur_ids
        ]

        pgbulk.copy(
            model_type,
            new_indirect_instances,
        )
