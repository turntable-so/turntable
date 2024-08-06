import json
from pathlib import Path

DEFAULT_CREDS_PATH = Path(Path.home(), ".vinyl.json")


class User:
    def __init__(self):
        self.credentials_path = DEFAULT_CREDS_PATH
        if not self.credentials_path.exists():
            raise ValueError("No credentials found. Please login first.")

    @property
    def user_info(self):
        with open(self.credentials_path, "r") as f:
            credentials = json.load(f)
            return {
                "email": credentials["email"],
                "user_id": credentials["user_id"],
            }
