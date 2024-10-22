from __future__ import annotations

import uuid

from django.contrib.postgres.fields import ArrayField
from django.db import connection, models
from django.db.models import Q
from pgvector.django import VectorField

from app.models.resources import Resource
from app.models.workspace import Workspace
from app.utils.urn import UrnAdjuster


class AssetContainer(models.Model):
    class AssetContainerType(models.TextChoices):
        WORKBOOK = "workbook"
        PROJECT = "project"
        DATABASE = "database"
        SCHEMA = "schema"
        WORKSPACE = "workspace"

    # pk
    id = models.CharField(max_length=255, primary_key=True, editable=False)
    type = models.CharField(max_length=255, choices=AssetContainerType.choices)
    name = models.TextField()
    description = models.TextField(null=True)

    # relationships
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)

    @property
    def assets(self):
        return Asset.objects.filter(containermembership__container_id=self.id)

    def adjust_urns(self):
        adjuster = UrnAdjuster(self.workspace.id)
        self.id = adjuster.adjust(self.id)

        return self

    @classmethod
    def get_for_resource(cls, resource_id: str, inclusive: bool = True):
        # return is the same for inclusive and exclusive
        # replace across resources, don't delete any
        if inclusive:
            return cls.objects.all()
        return cls.objects.none()


class Asset(models.Model):
    class AssetType(models.TextChoices):
        MODEL = "model"
        SOURCE = "source"
        SEED = "seed"
        ANALYSIS = "analysis"
        METRIC = "metric"
        SNAPSHOT = "snapshot"
        VIEW = "view"
        CHART = "chart"
        DASHBOARD = "dashboard"
        DATASET = "dataset"

    class MaterializationType(models.TextChoices):
        VIEW = "view"
        TABLE = "table"
        MATERIALIZED_VIEW = "materialized_view"
        EPHEMERAL = "ephemeral"

    # pk
    id = models.TextField(primary_key=True, editable=False)

    # fields
    type = models.CharField(max_length=20, choices=AssetType.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=255, null=True)
    description = models.TextField(null=True)
    ai_description = models.TextField(null=True)
    sql = models.TextField(null=True)
    config = models.JSONField(null=True)
    unique_name = models.TextField(null=True)
    tags = ArrayField(models.CharField(max_length=255), blank=True, null=True)
    tests = ArrayField(models.TextField(), blank=True, null=True)
    materialization = models.TextField(null=True, choices=MaterializationType.choices)
    db_location = ArrayField(models.CharField(max_length=255), blank=True, null=True)
    is_indirect = models.BooleanField(default=False)

    # relationships
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)

    @property
    def containers(self):
        return AssetContainer.objects.filter(containermembership__asset_id=self.id)

    @property
    def dataset(self) -> str:
        if self.db_location and len(self.db_location) > 0:
            return self.db_location[0]
        else:
            return ""

    @property
    def schema(self) -> str:
        if self.db_location and len(self.db_location) > 1:
            return self.db_location[1]
        else:
            return ""

    @property
    def table_name(self) -> str:
        if self.db_location and len(self.db_location) > 2:
            return self.db_location[2]
        else:
            return ""

    @property
    def resource_type(self) -> str:
        if self.resource:
            return self.resource.details.subtype

    @property
    def resource_subtype(self) -> str:
        if self.resource:
            return self.resource.subtype

    @property
    def resource_has_dbt(self) -> bool:
        if self.resource:
            return self.resource.has_dbt
        return False

    @property
    def subtype(self) -> str:
        if self.resource:
            return self.resource.subtype

    @property
    def num_columns(self) -> int:
        return self.columns.count()

    @property
    def resource_name(self) -> str:
        if self.resource:
            return self.resource.name
        return ""

    def adjust_urns(self):
        adjuster = UrnAdjuster(self.workspace.id)
        self.id = adjuster.adjust(self.id)

        return self

    def get_resource_ids(self) -> set[str]:
        return {self.resource.id}

    @classmethod
    def get_for_resource(cls, resource_id: str, inclusive: bool = True):
        # return is the same for inclusive and exclusive
        return cls.objects.filter(resource_id=resource_id)

    class Meta:
        indexes = [
            models.Index(fields=["workspace_id"]),
        ]

    def get_upstream_assets(self):
        links = AssetLink.objects.filter(target_id=self.id)
        return Asset.objects.filter(id__in=links.values_list("source_id", flat=True))


class ContainerMembership(models.Model):
    # pk
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # relationships
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    container = models.ForeignKey(AssetContainer, on_delete=models.CASCADE)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)

    def adjust_urns(self):
        adjuster = UrnAdjuster(self.workspace.id)
        self.asset_id = adjuster.adjust(self.asset_id)
        self.container_id = adjuster.adjust(self.container_id)

        return self

    @classmethod
    def get_for_resource(cls, resource_id: str, inclusive: bool = True):
        # return is the same for inclusive and exclusive
        # replace across resources, don't delete any
        if inclusive:
            return cls.objects.all()
        return cls.objects.none()


class Column(models.Model):
    # pk
    id = models.TextField(primary_key=True, editable=False)

    # fields
    name = models.TextField()
    type = models.TextField(null=True)
    nullable = models.BooleanField(null=True)
    description = models.TextField(null=True)
    ai_description = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tests = ArrayField(models.TextField(), blank=True, null=True)
    is_indirect = models.BooleanField(default=False)

    # relationships
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="columns")

    def adjust_urns(self):
        adjuster = UrnAdjuster(self.workspace.id)
        self.id = adjuster.adjust(self.id)
        self.asset_id = adjuster.adjust(self.asset_id)

        return self

    def get_resource_ids(self) -> set[str]:
        return {self.asset.resource.id}

    @property
    def is_unused(self):
        from app.models.metadata import (
            ColumnLink,
        )

        return not ColumnLink.objects.filter(Q(source=self)).exists()

    @classmethod
    def get_for_resource(cls, resource_id: str, inclusive: bool = True):
        # return is the same for inclusive and exclusive
        return cls.objects.filter(asset__resource_id=resource_id)

    class Meta:
        indexes = [
            models.Index(fields=["workspace_id"]),
            models.Index(fields=["asset_id"]),
        ]


class AssetLink(models.Model):
    class LineageQuery:
        PREDECESSOR_QUERY = """
WITH RECURSIVE traversed AS (
    SELECT
        source_id,
        target_id,
        1 AS depth
    FROM app_assetlink as a
    WHERE a.target_id = %(id)s and a.workspace_id = %(workspace_id)s

    UNION ALL

    SELECT        
        a.source_id,
        a.target_id,
        t.depth + 1
    FROM traversed as t
    JOIN app_assetlink as a ON a.target_id = t.source_id
    WHERE t.depth + 1 <= %(predecessor_depth)s and a.workspace_id = %(workspace_id)s
  )
SELECT
    source_id,
    target_id
FROM traversed
"""

        SUCCESSOR_QUERY = """
WITH RECURSIVE traversed AS (
    SELECT
        source_id,
        target_id,
        1 AS depth
    FROM app_assetlink as a
    WHERE a.source_id = %(id)s and a.workspace_id = %(workspace_id)s

    UNION ALL

    SELECT
        a.source_id,
        a.target_id,
        t.depth + 1
    FROM traversed as t
    JOIN app_assetlink as a ON a.source_id = t.target_id
    where t.depth + 1 <= %(successor_depth)s and a.workspace_id = %(workspace_id)s
)
SELECT
    source_id,
    target_id
FROM traversed
"""

    # pk
    id = models.TextField(primary_key=True, editable=False)

    # relationships
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    source = models.ForeignKey(
        Asset, on_delete=models.CASCADE, related_name="source_links"
    )
    target = models.ForeignKey(
        Asset, on_delete=models.CASCADE, related_name="target_links"
    )

    source_resource = models.ForeignKey(
        Resource, on_delete=models.CASCADE, related_name="source_resources", null=True
    )
    target_resource = models.ForeignKey(
        Resource, on_delete=models.CASCADE, related_name="target_resources", null=True
    )

    def adjust_urns(self):
        adjuster = UrnAdjuster(self.workspace.id)
        self.id = adjuster.adjust(self.id)
        self.source_id = adjuster.adjust(self.source_id)
        self.target_id = adjuster.adjust(self.target_id)

        return self

    @classmethod
    def successors(cls, workspace_id: str, asset_id: str, depth: int = 1):
        if depth == 0:
            return []

        with connection.cursor() as cursor:
            cursor.execute(
                cls.LineageQuery.SUCCESSOR_QUERY,
                {
                    "id": asset_id,
                    "workspace_id": workspace_id,
                    "successor_depth": depth,
                },
            )
            rows = cursor.fetchall()
        assets = set()
        for row in rows:
            assets.add(row[0])
            assets.add(row[1])
        return list(assets - set([asset_id]))

    @classmethod
    def predecessors(cls, workspace_id: str, asset_id: str, depth: int = 1):
        if depth == 0:
            return []
        with connection.cursor() as cursor:
            cursor.execute(
                cls.LineageQuery.PREDECESSOR_QUERY,
                {
                    "id": asset_id,
                    "workspace_id": workspace_id,
                    "predecessor_depth": depth,
                },
            )
            assets = {item for row in cursor.fetchall() for item in row}
        return list(assets - set([asset_id]))

    @classmethod
    def relatives(
        cls,
        workspace_id: str,
        asset_id: str,
        predecessor_depth: int = 1,
        successor_depth: int = 1,
    ):
        if predecessor_depth == 0 and successor_depth == 0:
            return []
        elif predecessor_depth == 0:
            return cls.successors(workspace_id, asset_id, successor_depth)
        elif successor_depth == 0:
            return cls.predecessors(workspace_id, asset_id, predecessor_depth)

        with connection.cursor() as cursor:
            cursor.execute(
                f"({cls.LineageQuery.PREDECESSOR_QUERY}) UNION ({cls.LineageQuery.SUCCESSOR_QUERY})",
                {
                    "id": asset_id,
                    "workspace_id": workspace_id,
                    "predecessor_depth": predecessor_depth,
                    "successor_depth": successor_depth,
                },
            )
            assets = {item for row in cursor.fetchall() for item in row}
        return list(assets - set([asset_id]))

    @classmethod
    def dynamic_successors(
        cls,
        workspace_id: str,
        asset_depth_dict: dict[int, list[str]],
        max_depth: int,
        exclude_resource_ids: list[str],
    ):
        if max_depth == 0:
            return []
        params = []
        query = """
WITH RECURSIVE traversed AS (
    SELECT
        source_id,
        target_id,
        CASE """

        # add depths
        for depth, assets in asset_depth_dict.items():
            if len(assets) > 0 and max_depth - depth > 0:
                query += "WHEN source_id IN ("
                query += ",".join(["%s" for asset in assets])
                params.extend(assets)
                query += ") THEN %s "
                params.append(depth + 1)

        query += "ELSE NULL END AS depth"

        # add conditions
        query += """
    FROM app_assetlink as a
    WHERE a.source_id IN ("""
        query += ",".join(["%s" for asset in assets])
        params.extend(assets)
        query += ") and a.workspace_id = %s"
        params.append(workspace_id)
        if exclude_resource_ids:
            query += " AND a.target_resource_id NOT IN ("
            query += ",".join(["%s" for resource_id in exclude_resource_ids]) + ") "
            params.extend(exclude_resource_ids)

        # add union
        query += """
    UNION ALL

    SELECT
        a.source_id,
        a.target_id,
        t.depth + 1
    FROM traversed as t
    JOIN app_assetlink as a ON a.source_id = t.target_id
    WHERE t.depth + 1 <= %s and a.workspace_id = %s
"""
        params.append(max_depth)
        params.append(workspace_id)

        if exclude_resource_ids:
            query += " AND a.target_resource_id NOT IN ("
            query += ",".join(["%s" for resource_id in exclude_resource_ids]) + ") "
            params.extend(exclude_resource_ids)

        query += """
)

SELECT
    source_id,
    target_id
FROM traversed
"""
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            assets = {item for row in cursor.fetchall() for item in row}
        return list(assets - set(asset_depth_dict.keys()))

    def get_resource_ids(self) -> set[str]:
        return set([self.source.resource.id, self.target.resource.id])

    @classmethod
    def get_for_resource(cls, resource_id: str, inclusive: bool = True):
        conditions = (
            Q(source__resource_id=resource_id),
            Q(target__resource_id=resource_id),
        )
        if inclusive:
            return cls.objects.filter(conditions[0] | conditions[1])
        return cls.objects.filter(conditions[0] & conditions[1])

    class Meta:
        indexes = [
            models.Index(fields=["source_id", "target_id"]),
            models.Index(fields=["workspace_id"]),
        ]


class ColumnLink(models.Model):
    class LineageType(models.TextChoices):
        ALL = "all"
        DIRECT_ONLY = "direct_only"

        def connection_types(self):
            if self == self.ALL:
                return []
            return ["as_is", "transform"]

    # pk
    id = models.TextField(primary_key=True, editable=False)

    # fields
    lineage_type = models.CharField(
        max_length=255, choices=LineageType.choices, null=True
    )
    connection_types = ArrayField(
        models.CharField(max_length=255), blank=True, null=True
    )
    confidence = models.FloatField(null=True)

    # relationships
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    source = models.ForeignKey(
        Column, on_delete=models.CASCADE, related_name="source_links"
    )
    target = models.ForeignKey(
        Column, on_delete=models.CASCADE, related_name="target_links"
    )

    def adjust_urns(self):
        adjuster = UrnAdjuster(self.workspace.id)
        self.id = adjuster.adjust(self.id)
        self.source_id = adjuster.adjust(self.source_id)
        self.target_id = adjuster.adjust(self.target_id)

        return self

    @classmethod
    def get_for_resource(cls, resource_id: str, inclusive: bool = True):
        conditions = (
            Q(source__asset__resource_id=resource_id),
            Q(target__asset__resource_id=resource_id),
        )
        if inclusive:
            return cls.objects.filter(conditions[0] | conditions[1])
        return cls.objects.filter(conditions[0] & conditions[1])

    class Meta:
        indexes = [
            models.Index(fields=["workspace_id"]),
            models.Index(fields=["source_id"]),
            models.Index(fields=["target_id"]),
        ]


class AssetError(models.Model):
    # pk
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # fields
    created_at = models.DateTimeField(auto_now_add=True)
    error = models.JSONField(null=True)
    lineage_type = models.TextField(null=True)

    # relationships
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, null=True)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)

    def adjust_urns(self):
        adjuster = UrnAdjuster(self.workspace.id)
        self.asset_id = adjuster.adjust(self.asset_id)

        return self

    @classmethod
    def get_for_resource(cls, resource_id: str, inclusive: bool = True):
        # return is the same for inclusive and exclusive
        return cls.objects.filter(asset__resource_id=resource_id)

    class Meta:
        indexes = [
            models.Index(fields=["workspace_id"]),
        ]


class AssetEmbedding(models.Model):
    # pk
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # fields
    autocomplete_vector = VectorField(dimensions=1536, null=True)
    search_vector = VectorField(dimensions=1536, null=True)

    # relationships
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)

    def adjust_urns(self):
        adjuster = UrnAdjuster(self.workspace.id)
        self.asset_id = adjuster.adjust(self.asset_id)

        return self

    class Meta:
        indexes = [
            models.Index(fields=["workspace_id"]),
        ]
