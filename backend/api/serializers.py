from django.contrib.auth.models import Group, User
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
    column_count = serializers.IntegerField(read_only=True)
    unused_columns_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Asset
        fields = [
            "id",
            "name",
            "unique_name",
            "type",
            "resource_id",
            "column_count",
            "unused_columns_count",
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
            "repository",
            "project_path",
            "target_name",
            "threads",
            "version",
            "database",
            "schema",
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
        ]

    def get_is_cloned(self, obj):
        return obj.is_cloned

    def get_pull_request_url(self, obj):
        return obj.pull_request_url
