from django.db.models import Model


class UrnAdjuster:
    JOIN_KEY = ":"

    def __init__(self, workspace_id: str):
        self.workspace_id = workspace_id

    def is_adjusted(self, urn: str):
        return not urn.startswith("urn:li:")

    def adjust(self, urn: str):
        if self.is_adjusted(urn):
            return urn
        return f"{self.workspace_id}{self.JOIN_KEY}{urn}"

    def adjust_obj(self, obj: Model):
        if not hasattr(obj, "urn_adjust_fields"):
            raise ValueError(
                f"Model {obj.__class__.__name__} must have a urn_adjust_fields attribute"
            )
        for k in obj.urn_adjust_fields:
            cur_k = getattr(obj, k)
            new_k = self.adjust(cur_k)
            setattr(obj, k, new_k)

    def reverse(self, urn: str):
        if not self.is_adjusted(urn):
            return urn
        return urn.split(self.JOIN_KEY, 1)[1]
