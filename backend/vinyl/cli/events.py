import os
from enum import Enum

from dotenv import load_dotenv
from posthog import Posthog
from vinyl.cli.user import User

load_dotenv()


# Define your Event enum
class Event(Enum):
    LOGIN = "vinyl.login"
    SOURCE_GEN = " vinyl.source_gen"
    PROJECT_INIT = " vinyl.project_init"
    PREVIEW_MODEL = " vinyl.model.preview"
    PREVIEW_METRIC = " vinyl.metric.preview"
    DEPLOY = " vinyl.deploy"
    SERVE = " vinyl.serve"


class EventLogger:
    def __init__(self):
        if os.getenv("NO_POSTHOG_LOGGING") == "true":
            self.off = True
            return
        else:
            self.off = False
        self.user = User()
        self.posthog = Posthog(
            "phc_XL4KyheAjc4gJV4Fzpg1lbn7goFP1QNqsnNUhY1O1CU",
            host="https://us.posthog.com",
        )
        self.posthog.identify(
            self.user.user_info["user_id"],
            {"email": self.user.user_info["email"]},
        )

    def log_event(self, event: Event):
        if self.off:
            return
        self.posthog.capture(self.user.user_info["user_id"], event.value)
