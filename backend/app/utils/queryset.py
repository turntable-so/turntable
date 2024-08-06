from functools import wraps

from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.db.models import QuerySet


def treat_like_dot_first(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        queryset = func(*args, **kwargs)
        if queryset[1:2].exists():
            out = queryset[:1]
            out._queryset = queryset
            return out
        return None

    return wrapper


def treat_like_dot_get(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        queryset = func(*args, **kwargs)
        if queryset[:1].count() == 1:
            if queryset[1:2].exists():
                raise MultipleObjectsReturned("Multiple Objects found.")
            out = queryset[0]
            out._queryset = queryset
            return out
        else:
            raise ObjectDoesNotExist("No matching object found.")

    return wrapper


def get_with_queryset(queryset: QuerySet, *args, **kwargs):
    out = queryset.get(*args, **kwargs)
    out._queryset = queryset.filter(*args, **kwargs)[:1]
    return out


def earliest_with_queryset(queryset: QuerySet, *args):
    out = queryset.earliest(*args)
    if args:
        out._queryset = queryset.order_by(*args)
    else:
        get_latest_by = queryset.model._meta.get_latest_by
        if not isinstance(get_latest_by, list):
            get_latest_by = [get_latest_by]
        get_earliest_by = []
        for field in get_latest_by:
            if field[0] == "-":
                get_earliest_by.append(field[1:])
            else:
                get_earliest_by.append(f"-{field}")
        out._queryset = queryset.order_by(*get_earliest_by)
    return out


def latest_with_queryset(queryset: QuerySet, *args):
    out = queryset.latest(*args)
    if args:
        out._queryset = queryset.order_by(*args)
    else:
        get_latest_by = queryset.model._meta.get_latest_by
        if not isinstance(get_latest_by, list):
            get_latest_by = [get_latest_by]
        out._queryset = queryset.order_by(*get_latest_by)
    return out


def first_with_queryset(queryset: QuerySet, *args, **kwargs):
    out = queryset.first(*args, **kwargs)
    if out:
        out._queryset = queryset.filter(*args, **kwargs)[:1]
        return out
    else:
        return None
