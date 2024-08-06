from dotenv import load_dotenv
import os
import ibis
import orjson
import pandas as pd
from workflows.hatchet import hatchet
from hatchet_sdk import Context
from django.core.files.base import ContentFile


load_dotenv()

from app.models import Block, Resource


def df_to_json(df: pd.DataFrame) -> str:
    data = df.to_json(orient="records")
    column_types = df.dtypes.apply(lambda x: x.name).to_dict()
    return orjson.dumps(
        {
            "data": orjson.loads(data),
            "column_types": column_types,
        }
    )


# inputs
# - query: str
# - block_id: int
# - resource_id: int
@hatchet.workflow(on_events=["execute_query"], timeout="2m")
class ExecuteQueryWorkflow:

    @hatchet.step()
    def execute_query(self, context: Context):
        os.environ["AWS_QUERYSTRING_AUTH"] = "True"
        os.environ["AWS_QUERYSTRING_EXPIRE"] = (
            "60"  # 60 second expirationAWS_S3_ENDPOINT_URL
        )
        os.environ["AWS_S3_ENDPOINT_URL"] = "localhost:9000"
        query = context.workflow_input()["query"]
        resource_id = context.workflow_input()["resource_id"]
        block_id = context.workflow_input()["block_id"]
        if not query:
            return {"error": "query is empty"}
        if not resource_id:
            return {"error": "resource_id is empty"}
        if not block_id:
            return {"error": "block_id is empty"}

        resource = Resource.objects.get(id=resource_id)
        block, created = Block.objects.get_or_create(id=block_id)
        connect = ibis.duckdb.connect(resource.config["file_path"], read_only=True)
        table = connect.sql(query)
        df = table.execute()
        query_results = df_to_json(df)

        query_results_file = ContentFile(query_results)
        block.results.save(f"{block_id}.json", query_results_file, save=True)
        block.refresh_from_db()
        signed_url = block.results.url
        return {"status": "success", "signed_url": signed_url}
