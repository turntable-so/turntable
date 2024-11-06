import json
import uuid

import pandas as pd
from django.core.files.base import ContentFile
from django.db import models
from django.utils import timezone

from app.models.git_connections import Branch
from app.models.resources import DBTResource, Resource
from app.models.workspace import Workspace
from app.services.storage_backends import CustomS3Boto3Storage
from vinyl.lib.utils.query import _QUERY_LIMIT


def query_to_json(df: pd.DataFrame, columns: dict[str, str]) -> str:
    data = df.to_json(orient="records")
    return f'{{"data": {data}, "column_types": {json.dumps(columns)}}}'


class Project(Branch):
    name = models.CharField(max_length=255)
    dbtresource = models.ForeignKey(
        DBTResource,
        on_delete=models.CASCADE,
    )

    def _code_repo_path(self, isolate: bool = False):
        return super()._code_repo_path(isolate, self.dbtresource.id)


class Query(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    sql = models.TextField(null=True)
    results = models.FileField(
        upload_to="query_results/", null=True, storage=CustomS3Boto3Storage()
    )
    resource = models.ForeignKey(
        Resource,
        on_delete=models.CASCADE,
    )

    # relationships
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)

    def run(self, limit: int | None = _QUERY_LIMIT):
        connector = self.resource.details.get_connector()
        df, columns = connector.run_query(self.sql, limit=limit)
        query_results = query_to_json(df, columns)

        query_results_file = ContentFile(query_results)
        self.results.save(f"{self.id}.json", query_results_file, save=True)
        self.refresh_from_db()
        signed_url = self.results.url
        return {"status": "success", "signed_url": signed_url}


class DBTQuery(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    dbt_sql = models.TextField(null=True)
    results = models.FileField(
        upload_to="dbt_query_results/", null=True, storage=CustomS3Boto3Storage()
    )
    dbtresource = models.ForeignKey(
        DBTResource,
        on_delete=models.CASCADE,
    )

    # relationships
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)

    def run(
        self,
        use_fast_compile: bool = True,
        limit: int | None = _QUERY_LIMIT,
    ):
        project_id = self.project.id if self.project else None
        with self.dbtresource.dbt_repo_context(project_id) as (
            dbtproj,
            project_path,
            _,
        ):
            connector = self.dbtresource.resource.details.get_connector()
            sql = None
            if use_fast_compile:
                sql = dbtproj.fast_compile(self.dbt_sql)
            if sql is None:
                sql = dbtproj.preview(self.dbt_sql, limit=limit, data=False)

            df, columns = connector.run_query(sql, limit=limit)
            query_results = query_to_json(df, columns)

            query_results_file = ContentFile(query_results)
            self.results.save(f"{self.id}.json", query_results_file, save=True)
            self.refresh_from_db()
            signed_url = self.results.url
            return {"status": "success", "signed_url": signed_url}
