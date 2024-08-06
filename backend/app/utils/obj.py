import datetime
import uuid
from collections import defaultdict

import numpy as np
from django.db.models import Model, QuerySet

DJANGO_FIELD_SEPARATOR = "__"

ID_FIELD = "id"


def make_values_serializable(val):
    if isinstance(val, dict):
        return {k: make_values_serializable(v) for k, v in val.items()}
    elif isinstance(val, list):
        return [make_values_serializable(item) for item in val]
    elif isinstance(val, uuid.UUID):
        return str(val)
    elif isinstance(val, np.ndarray):
        return make_values_serializable(val.tolist())
    elif isinstance(val, datetime.datetime):
        return val.isoformat()
    return val


def unflatten_dict(d, sep=DJANGO_FIELD_SEPARATOR):
    result_dict = {}
    for key, value in d.items():
        keys = key.split(sep)
        current_dict = result_dict
        for sub_key in keys[:-1]:
            current_dict = current_dict.setdefault(sub_key, {})
        if keys[-1] in current_dict:
            if not isinstance(current_dict[keys[-1]], list):
                current_dict[keys[-1]] = [current_dict[keys[-1]]]
            if value not in current_dict[keys[-1]]:
                current_dict[keys[-1]].append(value)
        else:
            current_dict[keys[-1]] = value
    return result_dict


def merge_values(existing_value, new_value):
    if not isinstance(existing_value, list):
        existing_value = [existing_value]
    if isinstance(new_value, list):
        existing_value.extend(val for val in new_value if val not in existing_value)
    elif new_value not in existing_value:
        existing_value.append(new_value)
    return existing_value


def group_and_merge(flattened_data, id_key=ID_FIELD, sep=DJANGO_FIELD_SEPARATOR):
    grouped_data = defaultdict(lambda: defaultdict(list))

    for item in flattened_data:
        item_id = item[id_key]
        unflattened_item = unflatten_dict(item, sep)
        for k, v in unflattened_item.items():
            if k != id_key:
                grouped_data[item_id][k] = merge_values(grouped_data[item_id][k], v)

    merged_data = [
        {
            id_key: item_id,
            **{
                k: (v[0] if isinstance(v, list) and len(v) == 1 else v)
                for k, v in fields.items()
            },
        }
        for item_id, fields in grouped_data.items()
    ]

    return merged_data


def convert_to_dict(obj: QuerySet | Model, serializable=True):
    converted = False
    if not isinstance(obj, (QuerySet, Model)):
        raise ValueError("Expected a QuerySet or Model object")
    elif isinstance(obj, Model):
        converted = True
        obj = obj._queryset

    if obj is None:
        return {}

    deferred_loading = obj.query.deferred_loading
    if deferred_loading[1] is False:
        base_out = [v for v in obj.values(*deferred_loading[0])]
    else:
        raise NotImplementedError("Not implemented for deferred loading")

    if serializable:
        base_out = make_values_serializable(base_out)
    out = group_and_merge(base_out)
    if converted:
        # If the input was a Model object, return a single dict rather than a list
        out = out[0]

    return out


def insert(model: Model, dicts: list[dict]):
    objs = []
    for dict_ in dicts:
        obj = model(**{k: v for k, v in dict_.items() if k != ID_FIELD})
        # need to handle ID explicitly in case the field is not editable
        if ID_FIELD in dict_:
            setattr(obj, ID_FIELD, dict_[ID_FIELD])
        objs.append(obj)
    model.objects.bulk_create(objs)
