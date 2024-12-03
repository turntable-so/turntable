import json
import os

import pytest
from litellm import OpenAI

from ai.core.chat import stream_chat_completion
from ai.core.models import ChatRequestBody
from app.models.resources import DBTCoreDetails


# run manually with "pytest -s -v -k TestEvals -n 2"
class TestEvals:
    @pytest.fixture
    def local_postgres_dbtresource(self, local_postgres):
        return DBTCoreDetails.get_job_dbtresource(
            workspace_id=local_postgres.workspace.id,
            resource_id=local_postgres.id,
        )

    @pytest.fixture
    def openai_client(self):
        return OpenAI()

    @staticmethod
    def _get_dataset():
        data = []
        dataset_dir = "ai/evals/dataset"
        for filename in os.listdir(dataset_dir):
            if filename.endswith(".json"):
                with open(os.path.join(dataset_dir, filename), "r") as f:
                    json_data = json.load(f)
                    data.append(json_data)
        return data

    def _assert_output(self, output, expected_output, openai_client):
        response = openai_client.chat.completions.create(
            model="o1-preview",
            messages=[
                {
                    "role": "user",
                    "content": f"""You must determine if the output is close to the expected output. Close in this context means that the output is somewhat similar to the expected output, as long as it is not completely wrong.
Here is the output:

{output}

Here is the expected output:

{expected_output}

Please answer in the following JSON format:

{{"result": "true" or "false", "explanation": "explanation of why the result is true or false"}}
""",
                }
            ],
        )
        json_response = json.loads(response.choices[0].message.content)
        assert json_response["result"] == "true"

    @pytest.mark.manual
    @pytest.mark.parametrize("data_row", _get_dataset())
    def test_eval(
        self, data_row, local_postgres_dbtresource, openai_client, local_postgres
    ):
        input_data = ChatRequestBody(**data_row["input"])
        expected_output = data_row["output"]
        stream = stream_chat_completion(
            payload=input_data,
            dbt_details=local_postgres_dbtresource,
            workspace=local_postgres.workspace,
        )
        output = "".join(chunk for chunk in stream)
        self._assert_output(output, expected_output, openai_client)
