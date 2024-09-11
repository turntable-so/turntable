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
    GithubInstallation,
    LookerDetails,
    Notebook,
    PostgresDetails,
    Resource,
    ResourceDetails,
    SnowflakeDetails,
    TableauDetails,
    User,
    Workspace,
    WorkspaceGroup,
)
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


class GithubInstallationSerializer(serializers.ModelSerializer):
    class Meta:
        model = GithubInstallation
        fields = [
            "id",
            "workspace_id",
            "user_id",
            "ssh_key",
            "git_url",
            "git_repo_type",
            "main_git_branch",
            "name",
        ]


class UserSerializer(serializers.HyperlinkedModelSerializer):
    current_workspace = serializers.SerializerMethodField()
    workspace_groups = WorkspaceGroupSerializer(many=True, read_only=True)

    def get_current_workspace(self, obj):
        current_workspace = obj.current_workspace()
        if current_workspace:
            return WorkspaceSerializer(current_workspace, context=self.context).data
        return None

    class Meta:
        model = User
        fields = ["id", "email", "current_workspace", "workspaces", "workspace_groups"]
        extra_kwargs = {
            "url": {"view_name": "user-detail"},
            "workspaces": {
                "view_name": "workspace-detail",
                "many": True,
                "read_only": True,
            },
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
        ]


# minified asset serializers for listing in the asset tree
class AssetIndexSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = [
            "id",
            "unique_name",
            "name",
            "type",
            "tags",
        ]


class AssetSerializer(serializers.ModelSerializer):
    # columns = ColumnSerializer(many=True, read_only=True)
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
            # "columns",
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
        fields = ["base_url", "client_id", "client_secret", "resource"]


class BigQueryDetailsSerializer(ResourceDetailsSerializer):
    class Meta:
        model = BigqueryDetails
        fields = ["service_account", "schema_include"]


class SnowflakeDetailsSerializer(ResourceDetailsSerializer):
    class Meta:
        model = SnowflakeDetails
        fields = ["account", "username", "password", "warehouse", "role"]


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
        fields = ["username", "password", "connect_uri"]


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


class DBTCoreDetailsSerializer(ResourceDetailsSerializer):
    version = DBTVersionField([(v, v.value) for v in DBTVersion])

    class Meta:
        model = DBTCoreDetails
        fields = [
            "git_repo_url",
            "main_git_branch",
            "deploy_key",
            "project_path",
            "threads",
            "version",
            "database",
            "schema",
        ]


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
