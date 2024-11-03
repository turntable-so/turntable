from django.apps import AppConfig


# Define a function to execute when a task starts
def task_started_handler(sender=None, task_id=None, **kwargs):
    pass
    # print(dir(sender))
    # print(f"Task {sender.name} is about to start!")


class TurntableAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app"

    def ready(self):
        import app.signals  # noqa
