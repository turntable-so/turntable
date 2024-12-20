import json
import os
import time
import uuid
from datetime import UTC, datetime, timedelta

from celery import current_app, states
from celery.result import AsyncResult
from croniter import croniter
from django.contrib.postgres.fields import ArrayField
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import models

# Use a window function to rank tasks by date within each periodic_task_name
from django.db.models import Window
from django.db.models.functions import RowNumber
from django_celery_beat.models import ClockedSchedule, CrontabSchedule, PeriodicTask
from django_celery_results.models import TaskResult
from polymorphic.models import PolymorphicModel

from app.models.project import Project
from app.models.resources import DBTResource, Resource
from app.models.settings import StorageSettings
from app.models.workspace import Workspace
from app.services.storage_backends import CustomFileField
from app.utils.fields import encrypt
from app.workflows.metadata import sync_metadata
from app.workflows.orchestration import run_dbt_commands

TASK_START_TIMEOUT = 10
TASK_START_POLLING_INTERVAL = 0.1


def get_periodic_task_key(periodic_task_name: str) -> str:
    return f"periodic_task_{periodic_task_name}"


class WorkflowType(models.TextChoices):
    CRON = "cron", "Cron"
    ONE_TIME = "one_time", "One Time"
    WEBHOOK = "webhook", "Webhook"


def uuid_str():
    return str(uuid.uuid4())


class ScheduledWorkflow(PolymorphicModel):
    id = models.CharField(primary_key=True, default=uuid_str, max_length=36)
    workflow_type = models.CharField(
        choices=WorkflowType.choices, max_length=255, editable=False
    )
    one_off = models.BooleanField(null=True)

    # relationships
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    clocked = models.OneToOneField(ClockedSchedule, on_delete=models.CASCADE, null=True)
    crontab = models.OneToOneField(CrontabSchedule, on_delete=models.CASCADE, null=True)
    periodic_task = models.OneToOneField(
        PeriodicTask, on_delete=models.CASCADE, null=True
    )
    hmac_secret_key = encrypt(models.CharField(max_length=255, null=True))

    # derived fields
    aggregation_identifier = models.CharField(
        max_length=64,
        editable=False,
        db_comment="The identifier of the periodic task that determines which other workflows this should be aggregated with in the frontend",
    )

    def clean(self):
        if self.workflow_type == WorkflowType.WEBHOOK:
            if self.crontab is not None or self.clocked is not None:
                raise ValidationError(
                    "Crontab and clocked must be None for webhook workflows"
                )
            if self.hmac_secret_key is None:
                raise ValidationError(
                    "HMAC secret key must be set for webhook workflows"
                )
        elif (self.clocked is None) == (self.crontab is None):
            raise ValidationError("Exactly one of clocked and crontab must be set")
        if not self.workflow_type:
            self.workflow_type = (
                WorkflowType.ONE_TIME if self.clocked else WorkflowType.CRON
            )
        elif self.workflow_type == WorkflowType.CRON and self.crontab is None:
            raise ValidationError("Crontab must be set for cron workflows")
        elif self.workflow_type == WorkflowType.ONE_TIME and self.clocked is None:
            raise ValidationError("Clocked must be set for one-time workflows")
        if self.one_off is None:
            self.one_off = self.workflow_type == WorkflowType.ONE_TIME
        if not self.one_off and self.clocked is not None:
            raise ValidationError("Clocked workflows cannot have one_off set to False")

    @property
    def workflow(self):
        raise NotImplementedError

    @property
    def kwargs(self):
        return {}

    @property
    def scheduling_excluded_fields(self):
        return {
            "id",
            "workflow_type",
            "periodic_task_id",
            "crontab_id",
            "clocked_id",
            "one_off",
            "polymorphic_ctype_id",
            "scheduledworkflow_ptr_id" "workflow_type",
        }

    def get_aggregation_identifier_dict(self):
        return {
            "TURNTABLE_SCHEDULED_WORKFLOW_NAME_***": self.workflow.name,
            "TURNTABLE_WORKFLOW_WORKSPACE_***": self.workspace_id,
            **self.kwargs,
        }

    def get_upcoming_tasks(self, n: int = 10):
        now = datetime.now(UTC)
        if self.workflow_type == WorkflowType.ONE_TIME:
            diff = self.clocked.clocked_time - now
            return [diff.total_seconds()]
        cron_expression_list = [
            str(self.crontab.minute),
            str(self.crontab.hour),
            str(self.crontab.day_of_week),
            str(self.crontab.day_of_month),
            str(self.crontab.month_of_year),
        ]
        cron_expression = " ".join(cron_expression_list)
        results = []
        now_timestamp = now.timestamp()
        for _ in range(n):
            cron = croniter(cron_expression, now_timestamp)
            next_time = cron.get_next()
            results.append(max(0, (next_time - now_timestamp)))
            now_timestamp = next_time
        return results

    def get_next_run_date(self) -> datetime:
        next_run_seconds = self.get_upcoming_tasks(1)[0]
        return datetime.now(UTC) + timedelta(seconds=next_run_seconds)

    def get_periodic_task_args(self):
        return {
            "name": self.id,
            "task": self.workflow.name,
            "kwargs": json.dumps(self.kwargs),
            "one_off": self.one_off,
            "clocked_id": self.clocked.id if self.clocked else None,
            "crontab_id": self.crontab.id if self.crontab else None,
        }

    def save(self, *args, **kwargs):
        SUPER_ONLY = "TURNTABLE_SUPER_ONLY"
        if SUPER_ONLY in kwargs:
            del kwargs[SUPER_ONLY]
            super().save(*args, **kwargs)
            return

        self.clean()

        # Calculate identifiers first
        if not self.aggregation_identifier:
            self.aggregation_identifier = str(self.id)
        if not self.workflow_type:
            self.workflow_type = (
                WorkflowType.ONE_TIME if self.clocked else WorkflowType.CRON
            )

        # Find and cleanup existing instance before creating new one
        if self.workflow_type != WorkflowType.WEBHOOK:
            if self.periodic_task:
                for key, value in self.get_periodic_task_args().items():
                    setattr(self.periodic_task, key, value)
                self.periodic_task.save()
            else:
                self.periodic_task = PeriodicTask.objects.create(
                    **self.get_periodic_task_args()
                )

        # Create new periodic task
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

        # ensure all one-to-one related objects are also deleted
        if self.periodic_task:
            self.periodic_task.delete()
        if self.crontab:
            self.crontab.delete()
        if self.clocked:
            self.clocked.delete()

    def await_next_id(
        self,
        timeout: float = TASK_START_TIMEOUT,
        polling_interval: float = TASK_START_POLLING_INTERVAL,
    ):
        seconds = 0
        key = get_periodic_task_key(self.id)
        while seconds < timeout:
            task_id = cache.get(key, "")
            if task_id:
                return task_id
            time.sleep(polling_interval)
            seconds += polling_interval

        raise Exception(f"Workflow did not start in timeout of {timeout} seconds")

    def await_next_result(
        self,
        start_timeout: int = TASK_START_TIMEOUT,
        duration_timeout: int | None = None,
    ):
        task_id = self.await_next_id(start_timeout)
        if os.getenv("CUSTOM_CELERY_EAGER") == "true":
            result = TaskResult.objects.get(task_id=task_id).result
        else:
            result = AsyncResult(task_id).get(timeout=duration_timeout)
        return result, task_id

    def cancel_next(self, start_timeout: int = TASK_START_TIMEOUT):
        task_id = self.await_next_id(start_timeout)
        current_app.control.revoke(task_id, terminate=True)
        return True

    def most_recent(
        self,
        n: int | None = 1,
        successes_only: bool = False,
        failures_only: bool = False,
    ):
        return self.most_recent_multiple([self.id], n, successes_only, failures_only)

    @classmethod
    def most_recent_multiple(
        cls,
        ids: list[str],
        n: int | None = 1,
        successes_only: bool = False,
        failures_only: bool = False,
    ) -> list[TaskResult]:
        tasks = TaskResult.objects.prefetch_related("periodic_task")

        if len(ids) == 1:
            tasks = tasks.filter(periodic_task__aggregation_identifier=ids[0])
        else:
            tasks = tasks.filter(periodic_task__aggregation_identifier__in=ids)

        if successes_only:
            tasks = tasks.filter(status=states.SUCCESS)
        if failures_only:
            tasks = tasks.filter(status=states.FAILURE)

        tasks = tasks.order_by("-date_done")

        if n is None:
            return tasks
        elif len(ids) == 1:
            return tasks[:n]
        else:
            tasks = tasks.annotate(
                row_num=Window(
                    expression=RowNumber(),
                    partition_by=["periodic_task__aggregation_identifier"],
                    order_by="-date_done",
                )
            )
            return tasks.filter(row_num__lte=n)

    def schedule_now(self):
        now = datetime.now(tz=UTC)
        clocked = ClockedSchedule.objects.create(clocked_time=now)
        attrs = {
            k: v
            for k, v in self.__dict__.items()
            if not k.startswith("_") and k not in self.scheduling_excluded_fields
        }
        return type(self).objects.create(
            **attrs, workflow_type=WorkflowType.ONE_TIME, clocked=clocked
        )

    @classmethod
    def get_results_with_filters(
        cls,
        **kwargs,
    ):
        tasks = TaskResult.objects.filter(
            periodic_task__aggregation_identifier__in=cls.objects.filter(
                **kwargs
            ).values_list("aggregation_identifier", flat=True)
        )
        tasks = tasks.order_by("-date_done")
        return tasks


class MetadataSyncWorkflow(ScheduledWorkflow):
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)

    @property
    def workflow(self):
        return sync_metadata

    @property
    def kwargs(self):
        return {
            "workspace_id": str(self.workspace_id),
            "resource_id": str(self.resource_id),
        }


class DBTOrchestrator(ScheduledWorkflow):
    dbtresource = models.ForeignKey(
        DBTResource, on_delete=models.CASCADE, related_name="dbt_orchestrator"
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
    commands = ArrayField(models.TextField())
    save_artifacts = models.BooleanField(default=True)
    name = models.CharField(max_length=255, null=False, default="Job")

    @property
    def workflow(self):
        return run_dbt_commands

    @property
    def kwargs(self):
        return {
            "workspace_id": str(self.workspace_id),
            "resource_id": str(self.dbtresource_id),
            "dbtresource_id": str(self.dbtresource_id),
            "commands": self.commands,
            "project_id": str(self.project_id) if self.project_id else None,
            "save_artifacts": self.save_artifacts,
        }

    @classmethod
    def get_results_filters(cls, **kwargs):
        filters = super().get_results_filters(**kwargs)
        if id := kwargs.get("dbtresource_id"):
            filters["dbtresource_id"] = id
        return filters


class ArtifactType(models.TextChoices):
    # use label as the file name
    MANIFEST = "manifest", "manifest.json"
    CATALOG = "catalog", "catalog.json"
    TARGET = "target", "target.zip"


class TaskArtifact(models.Model):
    def custom_upload_to(instance, filename):
        """
        Determine the custom folder path based on the instance's resource_id.
        """
        folder_name = f"task_artifacts/{instance.workspace_id}/{instance.task_id}/"

        # Return the full file path
        return os.path.join(folder_name, filename)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    artifact = CustomFileField(
        upload_to=custom_upload_to,
        storage_category=StorageSettings.StorageCategories.METADATA,
    )
    artifact_type = models.CharField(choices=ArtifactType.choices, max_length=255)

    # relationships
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    task = models.OneToOneField(
        TaskResult,
        on_delete=models.CASCADE,
        to_field="task_id",
        related_name="artifact",
    )

    @property
    def storage_applies_to(self):
        return StorageSettings.StorageCategories.METADATA
