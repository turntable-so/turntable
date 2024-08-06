from __future__ import annotations

import uuid

from django.contrib.postgres.fields import ArrayField
from django.db import models
from pgvector.django import VectorField

from app.models.auth import Workspace
from app.models.resources import Resource


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

    # relationships
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, null=True)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, null=True)

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
            return self.resource.type

    @classmethod
    def get_for_resource(cls, resource_id: str):
        return cls.objects.filter(resource_id=resource_id)

    class Meta:
        indexes = [
            models.Index(fields=["workspace_id"]),
        ]


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

    # relationships
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, null=True)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)

    @classmethod
    def get_for_resource(cls, resource_id: str):
        return cls.objects.prefetch_related("resource").filter(
            asset__resource_id=resource_id
        )

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
        id,
        source_id AS node_id,
        1 AS depth
    FROM app_assetlink as a
    WHERE a.target_id = %(id)s and a.workspace_id = %(workspace_id)s

    UNION ALL

    SELECT
        a.id,
        a.source_id,
        t.depth + 1
    FROM traversed as t
    JOIN app_assetlink as a ON a.target_id = t.node_id
    WHERE t.depth <= %(depth)s and a.workspace_id = %(workspace_id)s
  )
  SELECT id
  FROM traversed;
"""

        SUCCESSOR_QUERY = """
WITH RECURSIVE traversed AS (
    SELECT
        id,
        target_id AS node_id,
        1 AS depth
    FROM app_assetlink as a
    WHERE a.source_id = %(id)s 

    UNION ALL

    SELECT
        a.id,
        a.target_id,
        t.depth + 1
    FROM traversed as t
    JOIN app_assetlink as a ON a.source_id = t.node_id
    where t.depth <= %(depth)s and a.workspace_id = %(workspace_id)s
)
SELECT id
FROM traversed
"""

    # pk
    id = models.TextField(primary_key=True, editable=False)

    # relationships
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, null=True)
    source = models.ForeignKey(
        Asset, on_delete=models.CASCADE, related_name="source_links"
    )
    target = models.ForeignKey(
        Asset, on_delete=models.CASCADE, related_name="target_links"
    )

    @classmethod
    def successors(cls, workspace_id: str, asset_id: str, depth: int = 5):
        if depth == 0:
            return []
        queryset = cls.objects.raw(
            cls.LineageQuery.SUCCESSOR_QUERY,
            {"id": asset_id, "workspace_id": workspace_id, "depth": depth - 1},
        )
        queryset_values = [
            {"source_id": val.source_id, "target_id": val.target_id} for val in queryset
        ]
        assets = []
        for val in queryset_values:
            assets.append(val["source_id"])
            assets.append(val["target_id"])
        return list(set(assets) - set([asset_id]))

    @classmethod
    def predecessors(cls, workspace_id: str, asset_id: str, depth: int = 5):
        if depth == 0:
            return []
        queryset = cls.objects.raw(
            cls.LineageQuery.PREDECESSOR_QUERY,
            {"id": asset_id, "workspace_id": workspace_id, "depth": depth - 1},
        )
        queryset_values = [
            {"source_id": val.source_id, "target_id": val.target_id} for val in queryset
        ]
        assets = []
        for val in queryset_values:
            assets.append(val["source_id"])
            assets.append(val["target_id"])
        return list(set(assets) - set([asset_id]))

    @classmethod
    def get_for_resource(cls, resource_id: str):
        return (
            cls.objects.prefetch_related("resource")
            .filter(source__resource_id=resource_id)
            .filter(target__resource_id=resource_id)
        )

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
    lineage_type = models.CharField(max_length=255, choices=LineageType.choices)
    connection_types = ArrayField(
        models.CharField(max_length=255), blank=True, null=True
    )
    confidence = models.FloatField(null=True)

    # relationships
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, null=True)
    source = models.ForeignKey(
        Column, on_delete=models.CASCADE, related_name="source_links"
    )
    target = models.ForeignKey(
        Column, on_delete=models.CASCADE, related_name="target_links"
    )

    @classmethod
    def get_for_resource(cls, resource_id: str):
        return (
            cls.objects.prefetch_related("asset", "resource")
            .filter(source__asset__resource_id=resource_id)
            .filter(target__asset__resource_id=resource_id)
        )

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
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, null=True)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)

    class Meta:
        indexes = [
            models.Index(fields=["workspace_id"]),
        ]
