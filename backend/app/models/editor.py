import uuid

import orjson
import pandas as pd
from django.core.files.base import ContentFile
from django.db import models
from django.utils import timezone

from app.models.git_connections import Branch
from app.models.resources import DBTResource
from app.models.workspace import Workspace
from app.services.storage_backends import CustomS3Boto3Storage
from vinyl.lib.connect import _QUERY_LIMIT


class DBTQuery(models.Model):
    user_id = models.CharField(max_length=255)
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

    @classmethod
    def df_to_json(cls, df: pd.DataFrame) -> str:
        data = df.to_json(orient="records")
        column_types = df.dtypes.apply(lambda x: x.name).to_dict()
        return orjson.dumps(
            {
                "data": orjson.loads(data),
                "column_types": column_types,
            }
        )

    def run(
        self,
        use_fast_compile: bool = True,
        limit: int | None = _QUERY_LIMIT,
    ):
        branch_id = self.branch.id if self.branch else None
        with self.dbtresource.dbt_repo_context(branch_id) as (dbtproj, project_path, _):
            if use_fast_compile and (sql := dbtproj.fast_compile(self.dbt_sql)):
                connector = self.dbtresource.resource.details.get_connector()
                df = connector.sql_to_df(sql, limit=limit)
                query_results = self.df_to_json(df)
            else:
                query_results = dbtproj.preview(self.dbt_sql, limit=limit)

            query_results = f'{{"data": {query_results}}}'
            query_results_file = ContentFile(query_results)
            self.results.save(f"{self.id}.json", query_results_file, save=True)
            self.refresh_from_db()
            signed_url = self.results.url
            return {"status": "success", "signed_url": signed_url}
