import json
import os

import pytest

from ai.core.chat import stream_chat_completion
from ai.core.models import ChatRequestBody
from app.models.resources import DBTCoreDetails


def get_dataset():
    data = []
    dataset_dir = "ai/evals/dataset"
    for filename in os.listdir(dataset_dir):
        if filename.endswith(".json"):
            with open(os.path.join(dataset_dir, filename), "r") as f:
                json_data = json.load(f)
                data.append(json_data)
    return data


class TestEvals:
    @pytest.fixture
    def local_postgres_dbtresource(self, local_postgres):
        return DBTCoreDetails.get_job_dbtresource(
            workspace_id=local_postgres.workspace.id,
            resource_id=local_postgres.id,
        )

    @pytest.mark.parametrize("data_row", get_dataset())
    def test_eval(self, data_row, local_postgres_dbtresource):
        input_data = ChatRequestBody(**data_row["input"])
        expected_output = data_row["output"]

        stream = stream_chat_completion(
            payload=input_data, dbt_details=local_postgres_dbtresource
        )
        output = "".join(chunk for chunk in stream)

        assert output == expected_output
