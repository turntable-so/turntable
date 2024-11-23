import json
import os
import time
import uuid
from datetime import datetime, timezone

from celery import current_app, states
from celery.result import AsyncResult
from croniter import croniter
from django.contrib.postgres.fields import ArrayField
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import QuerySet
from django_celery_beat.models import ClockedSchedule, CrontabSchedule, PeriodicTask
from django_celery_results.models import TaskResult
from polymorphic.models import PolymorphicModel

from app.models.project import Project
from app.models.resources import DBTResource, Resource
from app.models.settings import StorageSettings
from app.models.workspace import Workspace
from app.services.storage_backends import CustomFileField
from app.workflows.metadata import sync_metadata
from app.workflows.orchestration import run_dbt_commands

TASK_START_TIMEOUT = 100
TASK_START_POLLING_INTERVAL = 0.1


def get_periodic_task_key(periodic_task_name: str) -> str:
    return f"periodic_task_{periodic_task_name}"


class WorkflowType(models.TextChoices):
    CRON = "cron", "Cron"
    ONE_TIME = "one_time", "One Time"


class ScheduledWorkflow(PolymorphicModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    workflow_type = models.CharField(
        choices=WorkflowType.choices, max_length=255, editable=False
    )
    one_off = models.BooleanField(null=True)

    # relationships
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    clocked = models.ForeignKey(ClockedSchedule, on_delete=models.CASCADE, null=True)
    crontab = models.ForeignKey(CrontabSchedule, on_delete=models.CASCADE, null=True)
    periodic_task = models.ForeignKey(PeriodicTask, on_delete=models.CASCADE, null=True)

    # derived fields
    replacement_identifier = models.CharField(
        max_length=64,
        editable=False,
        db_comment="The identifier of the periodic task that determines whether a new workflow should be created or an existing workflow should be updated",
    )
    aggregation_identifier = models.CharField(
        max_length=64,
        editable=False,
        db_comment="The identifier of the periodic task that determines which other workflows this should be aggregated with in the frontend",
    )

    def clean(self):
        if (self.clocked is None) == (self.crontab is None):
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
            "replacement_identifier",
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
        now = datetime.now(timezone.utc)
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

    def get_periodic_task_args(self):
        return {
            "name": self.replacement_identifier,
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
        custom_celery_eager = os.getenv("CUSTOM_CELERY_EAGER") == "true"

        self.clean()

        # Calculate identifiers first
        if not self.aggregation_identifier:
            self.aggregation_identifier = str(self.id)
        if not self.replacement_identifier:
            self.replacement_identifier = str(self.id)
        if not self.workflow_type:
            self.workflow_type = (
                WorkflowType.ONE_TIME if self.clocked else WorkflowType.CRON
            )

        # Find and cleanup existing instance before creating new one
        try:
            existing = type(self).objects.get(id=self.id) if self.id else None
            if existing:
                # Clean up the old periodic task
                PeriodicTask.objects.filter(
                    name=existing.replacement_identifier
                ).delete()

                # Clean up old crontab if it's not being used by any other workflows (in this case, not this workflow)
                if (
                    existing.crontab != self.crontab
                    and not type(self)
                    .objects.filter(crontab=existing.crontab)
                    .exclude(id=existing.id)
                    .exists()
                ):
                    existing.crontab.delete()
        except type(self).DoesNotExist:
            pass

        # Create new periodic task
        self.periodic_task = PeriodicTask.objects.create(
            **self.get_periodic_task_args()
        )

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

        # delete the periodic task
        self.periodic_task.delete()

        # delete the crontab if no other workflows are using it
        if (
            not type(self)
            .objects.filter(crontab=self.crontab)
            .exclude(id=self.id)
            .exists()
        ):
            self.crontab.delete()

    def await_next_id(
        self,
        timeout: float = TASK_START_TIMEOUT,
        polling_interval: float = TASK_START_POLLING_INTERVAL,
    ):
        seconds = 0
        key = get_periodic_task_key(self.replacement_identifier)
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
        try:
            tasks = TaskResult.objects.filter(
                periodic_task_name__in=type(self)
                .objects.filter(aggregation_identifier=self.aggregation_identifier)
                .values_list("replacement_identifier", flat=True)
            )
            if successes_only:
                tasks = tasks.filter(status=states.SUCCESS)
            if failures_only:
                tasks = tasks.filter(status=states.FAILURE)
            tasks = tasks.order_by("-date_done")
            if n is not None:
                tasks = tasks[:n]
            return tasks
        except TaskResult.DoesNotExist:
            return QuerySet()

    def schedule_now(self):
        now = datetime.now(tz=timezone.utc)
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
    def get_results_filters(cls, **kwargs):
        return {
            "workspace_id": kwargs.get("workspace_id"),
        }

    @classmethod
    def get_results(
        cls,
        **kwargs,
    ):
        filters = cls.get_results_filters(**kwargs)
        tasks = TaskResult.objects.filter(
            periodic_task_name__in=cls.objects.filter(**filters).values_list(
                "replacement_identifier", flat=True
            )
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
    task = models.ForeignKey(TaskResult, on_delete=models.CASCADE, to_field="task_id")

    @property
    def storage_applies_to(self):
        return StorageSettings.StorageCategories.METADATA
