import json

import orjson
from django.contrib.auth.models import Group
from django_celery_beat.models import CrontabSchedule
from django_celery_results.models import TaskResult
from djoser.serializers import UserCreateSerializer, UserSerializer
from invitations.utils import get_invitation_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from app.models import (
    Asset,
    AssetLink,
    BigqueryDetails,
    Block,
    Column,
    ColumnLink,
    DatabricksDetails,
    DBTCoreDetails,
    LookerDetails,
    Notebook,
    PostgresDetails,
    PowerBIDetails,
    RedshiftDetails,
    Repository,
    Resource,
    ResourceDetails,
    SnowflakeDetails,
    SSHKey,
    TableauDetails,
    User,
    Workspace,
    WorkspaceGroup,
)
from app.models.project import Project
from app.models.resources import MetabaseDetails
from app.models.workflows import DBTOrchestrator, ScheduledWorkflow, TaskArtifact
from app.workflows.utils import ABORTED, PREABORT_RESULT_KEY, AbortedException
from vinyl.lib.dbt_methods import DBTVersion

Invitation = get_invitation_model()


class UserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        model = User
        fields = ("id", "email")


class WorkspaceGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkspaceGroup
        fields = ["id", "name", "workspace_id"]


class InvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitation
        fields = ["id", "email", "inviter_id", "accepted"]


class UserSerializer(serializers.HyperlinkedModelSerializer):
    current_workspace = serializers.SerializerMethodField()
    workspace_groups = WorkspaceGroupSerializer(many=True, read_only=True)
    workspaces = serializers.SerializerMethodField()

    def get_current_workspace(self, obj):
        current_workspace = obj.current_workspace()
        if current_workspace:
            from api.serializers import WorkspaceSerializer

            return WorkspaceSerializer(current_workspace, context=self.context).data
        return None

    def get_workspaces(self, obj):
        from api.serializers import WorkspaceSerializer

        return WorkspaceSerializer(
            obj.workspaces.all(), many=True, context=self.context
        ).data

    class Meta:
        model = User
        fields = ["id", "email", "current_workspace", "workspaces", "workspace_groups"]
        extra_kwargs = {
            "url": {"view_name": "user-detail"},
            "workspace_groups": {
                "view_name": "workspacegroup-detail",
                "many": True,
                "read_only": True,
            },
        }


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        fields = UserCreateSerializer.Meta.fields

    def create(self, validated_data):
        user = super().create(validated_data)
        refresh = RefreshToken.for_user(user)
        self.tokens = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
        return user

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["tokens"] = self.tokens
        return representation


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ["url", "name"]


class WorkspaceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Workspace
        fields = ["id", "name", "icon_url", "icon_file", "member_count"]


class WorkspaceUserSerializer(serializers.ModelSerializer):
    workspace_groups = WorkspaceGroupSerializer(many=True)

    class Meta:
        model = User
        fields = ["id", "name", "workspace_groups", "email"]


class WorkspaceDetailSerializer(serializers.ModelSerializer):
    users = WorkspaceUserSerializer(many=True)

    class Meta:
        model = Workspace
        fields = ["id", "name", "icon_url", "icon_file", "users"]
        depth = 1


class ColumnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Column
        fields = [
            "id",
            "name",
            "type",
            "description",
            "ai_description",
            "created_at",
            "updated_at",
            "tests",
            "is_unused",
        ]


# minified asset serializers for listing in the asset tree
class AssetIndexSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = [
            "id",
            "name",
            "unique_name",
            "type",
            "resource_id",
        ]


class AssetSerializer(serializers.ModelSerializer):
    columns = serializers.SerializerMethodField()
    dataset = serializers.SerializerMethodField()
    schema = serializers.SerializerMethodField()
    table_name = serializers.SerializerMethodField()
    resource_type = serializers.SerializerMethodField()
    resource_id = serializers.PrimaryKeyRelatedField(
        source="resource.id", read_only=True
    )

    column_count = serializers.IntegerField(read_only=True)
    unused_columns_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Asset
        fields = [
            "id",
            "unique_name",
            "schema",
            "dataset",
            "table_name",
            "name",
            "columns",
            "description",
            "url",
            "type",
            "tags",
            "created_at",
            "updated_at",
            "tags",
            "tests",
            "materialization",
            "resource_type",
            "resource_subtype",
            "resource_has_dbt",
            "resource_name",
            "resource_id",
            "column_count",
            "unused_columns_count",
        ]

    def get_dataset(self, obj):
        return obj.dataset

    def get_schema(self, obj):
        return obj.schema

    def get_table_name(self, obj):
        return obj.table_name

    def get_resource_type(self, db):
        return db.resource_type

    def get_columns(self, obj):
        temp_columns = getattr(obj, "temp_columns", None)
        if temp_columns is not None:
            return ColumnSerializer(temp_columns, many=True).data
        return ColumnSerializer(obj.columns, many=True).data


class AssetLinkSerializer(serializers.ModelSerializer):
    source_id = serializers.PrimaryKeyRelatedField(
        queryset=Asset.objects.all(), source="source"
    )
    target_id = serializers.PrimaryKeyRelatedField(
        queryset=Asset.objects.all(), source="target"
    )

    class Meta:
        model = AssetLink
        fields = ["id", "source_id", "target_id"]


class ColumnLinkSerializer(serializers.ModelSerializer):
    source_id = serializers.PrimaryKeyRelatedField(
        queryset=Asset.objects.all(), source="source"
    )
    target_id = serializers.PrimaryKeyRelatedField(
        queryset=Asset.objects.all(), source="target"
    )

    class Meta:
        model = ColumnLink
        fields = ["id", "lineage_type", "connection_types", "source_id", "target_id"]


class LineageSerializer(serializers.Serializer):
    asset_id = serializers.UUIDField()
    assets = AssetSerializer(many=True)
    asset_links = AssetLinkSerializer(many=True)
    column_links = ColumnLinkSerializer(many=True)


class NotebookDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notebook
        fields = ["id", "title", "contents", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]


class NotebookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notebook
        fields = ["id", "title", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]


class ResourceDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResourceDetails
        fields = [
            "subtype",
            "config",
        ]


class LookerDetailsSerializer(ResourceDetailsSerializer):
    class Meta:
        model = LookerDetails
        fields = ["base_url", "client_id", "client_secret", "resource", "repository_id"]


class BigQueryDetailsSerializer(ResourceDetailsSerializer):
    bq_project_id = serializers.CharField(allow_null=True, required=False)

    class Meta:
        model = BigqueryDetails
        fields = ["service_account", "schema_include", "location", "bq_project_id"]


class SnowflakeDetailsSerializer(ResourceDetailsSerializer):
    class Meta:
        model = SnowflakeDetails
        fields = ["account", "username", "password", "warehouse", "role"]


class RedshiftDetailsSerializer(ResourceDetailsSerializer):
    class Meta:
        model = RedshiftDetails
        fields = ["host", "username", "password", "database", "port", "serverless"]


class PostgresDetailsSerializer(ResourceDetailsSerializer):
    class Meta:
        model = PostgresDetails
        fields = ["host", "username", "password", "database", "port"]


class DatabricksDetailsSerializer(ResourceDetailsSerializer):
    class Meta:
        model = DatabricksDetails
        fields = ["host", "token", "http_path"]


class TableauDetailsSerializer(ResourceDetailsSerializer):
    class Meta:
        model = TableauDetails
        fields = ["username", "password", "site", "connect_uri"]


class MetabaseDetailsSerializer(ResourceDetailsSerializer):
    class Meta:
        model = MetabaseDetails
        fields = ["username", "password", "connect_uri", "api_key", "jwt_shared_secret"]


class PowerBIDetailsSerializer(ResourceDetailsSerializer):
    class Meta:
        model = PowerBIDetails
        fields = [
            "client_id",
            "client_secret",
            "powerbi_tenant_id",
            "powerbi_workspace_id",
        ]


class DBTVersionField(serializers.ChoiceField):
    def to_representation(self, obj):
        if obj is None:
            return None
        if isinstance(obj, str):
            return obj
        return obj.value

    def to_internal_value(self, data):
        try:
            return DBTVersion(data)
        except ValueError:
            self.fail("invalid_choice", input=data)


class SSHKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = SSHKey
        fields = ["id", "public_key"]


class RepositorySerializer(serializers.ModelSerializer):
    ssh_key = SSHKeySerializer()

    class Meta:
        model = Repository
        fields = ["id", "main_branch_name", "git_repo_url", "ssh_key"]


class DBTCoreDetailsSerializer(ResourceDetailsSerializer):
    version = DBTVersionField([(v, v.value) for v in DBTVersion])
    repository = RepositorySerializer()

    class Meta:
        model = DBTCoreDetails
        fields = [
            "id",
            "repository",
            "project_path",
            "target_name",
            "threads",
            "version",
            "database",
            "schema",
            "environment",
        ]

    def update(self, instance, validated_data):
        repository_data = validated_data.pop("repository")
        instance.repository.git_repo_url = repository_data.get("git_repo_url")
        instance.repository.main_branch_name = repository_data.get("main_branch_name")
        instance.repository.save()

        instance.project_path = validated_data.get(
            "project_path", instance.project_path
        )
        instance.threads = validated_data.get("threads")
        instance.target_name = validated_data.get("target_name")
        instance.version = validated_data.get("version")
        instance.database = validated_data.get("database")
        instance.schema = validated_data.get("schema")
        instance.save()
        return instance


class BlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Block
        fields = ["id", "results", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]


class ResourceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Resource
        fields = [
            "id",
            "name",
            "updated_at",
            "type",
            "subtype",
            "last_synced",
            "status",
            "has_dbt",
        ]

    def get_last_synced(self, obj):
        return obj.last_synced

    def get_status(self, obj):
        return obj.status

    def get_subtype(self, obj):
        return obj.subtype

    def get_has_dbt(self, obj):
        return obj.has_dbt


class ProjectSerializer(serializers.ModelSerializer):
    is_cloned = serializers.SerializerMethodField()
    pull_request_url = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "branch_name",
            "schema",
            "read_only",
            "is_cloned",
            "pull_request_url",
            "source_branch",
        ]

    def get_is_cloned(self, obj):
        return obj.is_cloned

    def get_pull_request_url(self, obj):
        return obj.pull_request_url


class CrontabWorkflowSerializer(serializers.ModelSerializer):
    cron_str = serializers.CharField(required=False)
    name = serializers.CharField(required=False)
    workspace_id = serializers.PrimaryKeyRelatedField(
        queryset=Workspace.objects.all(), source="workspace"
    )

    class Meta:
        model = ScheduledWorkflow
        fields = ["id", "workspace_id", "cron_str"]

    def schedule_helper(self, cron_str):
        split_cron = cron_str.split(" ")
        crontab, _ = CrontabSchedule.objects.get_or_create(
            minute=split_cron[0],
            hour=split_cron[1],
            day_of_week=split_cron[2],
            day_of_month=split_cron[3],
            month_of_year=split_cron[4],
        )
        return crontab

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.crontab:
            data["cron_str"] = (
                f"{instance.crontab.minute} {instance.crontab.hour} {instance.crontab.day_of_week} {instance.crontab.day_of_month} {instance.crontab.month_of_year}"
            )
        return data

    def create(self, validated_data):
        if "cron_str" in validated_data:
            cron_str = validated_data.pop("cron_str")
            crontab = self.schedule_helper(cron_str)
            validated_data["crontab"] = crontab
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Update the crontab schedule if cron_str is provided
        if "cron_str" in validated_data:
            cron_str = validated_data.pop("cron_str")
            crontab = self.schedule_helper(cron_str)
            instance.crontab = crontab
            instance.save()

        return super().update(instance, validated_data)


class DBTOrchestratorSerializer(CrontabWorkflowSerializer):
    dbtresource_id = serializers.PrimaryKeyRelatedField(
        queryset=DBTCoreDetails.objects.all(), source="dbtresource"
    )
    commands = serializers.ListField(child=serializers.CharField())
    latest_run = serializers.SerializerMethodField()
    next_run = serializers.SerializerMethodField()

    class Meta:
        model = DBTOrchestrator
        fields = [
            "id",
            "dbtresource_id",
            "cron_str",
            "save_artifacts",
            "commands",
            "name",
            "latest_run",
            "next_run",
        ]

    def validate_commands(self, value):
        if not all(cmd.strip().startswith("dbt") for cmd in value):
            raise serializers.ValidationError("All commands must start with 'dbt'")
        return value

    def create(self, validated_data):
        if "cron_str" in validated_data:
            cron_str = validated_data.pop("cron_str")
            crontab = self.schedule_helper(cron_str)
            validated_data["crontab"] = crontab
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

    def get_latest_run(self, obj):
        latest_run = obj.most_recent(n=1).first()
        return TaskResultSerializer(latest_run).data if latest_run else None

    def get_next_run(self, obj):
        return obj.get_next_run_date()


class TaskArtifactSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskArtifact
        fields = ["id", "artifact", "artifact_type"]


class TaskListSerializer(serializers.ListSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._instance_cache = {i.task_id: i for i in self.instance if i is not None}


class TaskResultSerializer(serializers.ModelSerializer):
    artifacts = TaskArtifactSerializer(
        source="taskartifact_set", many=True, read_only=True
    )
    subtasks = serializers.SerializerMethodField()
    result = serializers.SerializerMethodField()
    traceback = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    task_args = serializers.SerializerMethodField()
    task_kwargs = serializers.SerializerMethodField()

    def _ensure_task_cached(self, task_ids: list[str]) -> None:
        """Fetch and cache any uncached tasks"""
        uncached_ids = set(task_ids) - set(self.context["task_cache"])
        if uncached_ids:
            new_tasks = TaskResult.objects.filter(task_id__in=uncached_ids)
            self.context["task_cache"].update(
                {task.task_id: task for task in new_tasks}
            )

    def _parse_meta(self, instance) -> dict | None:
        """Parse instance metadata, returning None if invalid"""
        if not hasattr(instance, "meta"):
            return None

        if isinstance(instance.meta, dict):
            return instance.meta

        try:
            return orjson.loads(instance.meta)
        except (json.JSONDecodeError, AttributeError):
            return None

    def _process_subtasks(self, children: list) -> list:
        """Process and serialize subtasks from children data"""
        # Extract valid task entries
        if not children:
            return []
        task_entries = [
            (child[0][0], child[1])  # (task_id, metadata)
            for child in children
            if isinstance(child[0], list)
        ]
        # Ensure all tasks are cached
        task_ids = [task_id for task_id, _ in task_entries]
        self._ensure_task_cached(task_ids)

        # Serialize available tasks
        tasks = TaskResultSerializer(
            [self.context["task_cache"].get(task_id) for task_id in task_ids],
            many=True,
            context=self.context,
        ).data

        # Apply additional metadata
        for task_data, (_, metadata) in zip(tasks, task_entries):
            if metadata:
                task_data.update(metadata)

        return tasks

    def _parse_json(self, data):
        if not data:
            return None
        try:
            return orjson.loads(data)
        except orjson.JSONDecodeError:
            return data

    def _was_aborted(self, obj, result_override: dict | None = None) -> bool:
        result = result_override or self._parse_json(obj.result)
        if "exc_type" in result and result["exc_type"] == AbortedException.__name__:
            return True
        return False

    def get_status(self, obj):
        # ignore status if the task was aborted
        if not self._was_aborted(obj):
            return obj.status
        return ABORTED

    def get_result(self, obj):
        # adjust result if the task was aborted
        result = self._parse_json(obj.result)
        if not self._was_aborted(obj, result):
            return result

        messages = result.get("exc_message", [None])
        if not messages or len(messages) != 1:
            return result

        preabort_results = self._parse_json(messages[0])[PREABORT_RESULT_KEY]
        return preabort_results.get(obj.task_id, None)

    def get_traceback(self, obj):
        # ignore traceback if the task was aborted
        result = self._parse_json(obj.result)
        if not self._was_aborted(result):
            return obj.traceback
        return None

    def get_task_args(self, obj):
        return self._parse_json(obj.task_args)

    def get_task_kwargs(self, obj):
        result = self._parse_json(obj.task_kwargs)
        return result

    def to_representation(self, instance):
        # Initialize cache if needed
        self.context.setdefault("task_cache", {})
        if instance is None:
            return None
        self.context["task_cache"][instance.task_id] = instance

        data = super().to_representation(instance)

        # Process subtasks if present
        meta = self._parse_meta(instance)
        if meta and "children" in meta:
            data["subtasks"] = self._process_subtasks(meta["children"])

        return data

    def get_job_id(self, obj):
        return obj.job_id

    def get_job_name(self, obj):
        return obj.job_name

    def get_subtasks(self, obj):
        return []

    class Meta:
        model = TaskResult
        list_serializer_class = TaskListSerializer
        fields = [
            "task_id",
            "status",
            "task_args",
            "task_kwargs",
            "result",
            "date_created",
            "date_done",
            "traceback",
            "artifacts",
            "subtasks",
        ]


class TaskResultWithJobSerializer(TaskResultSerializer):
    job_id = serializers.SerializerMethodField()
    job_name = serializers.SerializerMethodField()

    def get_job_id(self, obj):
        return obj.job_id

    def get_job_name(self, obj):
        return obj.job_name

    class Meta(TaskResultSerializer.Meta):
        fields = TaskResultSerializer.Meta.fields + ["job_id", "job_name"]
