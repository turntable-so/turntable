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
