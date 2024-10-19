import uuid
from urllib.parse import quote, unquote

import pytest

from app.models import Branch
from app.utils.test_utils import assert_ingest_output, require_env_vars
from app.utils.url import build_url
from workflows.metadata_sync import MetadataSyncWorkflow
from workflows.utils.debug import ContextDebugger


def safe_encode(s):
    return quote(s, safe="")


def safe_decode(s):
    return unquote(s)


@pytest.mark.django_db
@pytest.mark.usefixtures("force_isolate", "bypass_hatchet", "local_postgres")
@require_env_vars("SSHKEY_0_PUBLIC", "SSHKEY_0_PRIVATE")
class TestProjectViews:
    @pytest.fixture
    def encoded_filepath(self):
        return safe_encode("models/marts/customer360/customers.sql")

    def test_file_index(self, client):
        response = client.get("/project/files/")
        response_json = response.json()

        assert response.status_code == 200
        assert len(response_json["file_index"]) > 0

    def test_branches(self, client):
        response = client.get("/project/branches/")
        branches = response.json()

        assert response.status_code == 200
        assert branches["active_branch"] == "main"
        assert len(branches["branches"]) > 0

    def test_create_branch(self, client):
        response = client.post("/project/branches/", {"branch_name": "test"})
        assert response.status_code == 201
        assert response.json()["branch_name"] == "test"

    def test_switch_branch(self, client):
        response = client.post("/project/branches/", {"branch_name": "test"})
        response = client.patch("/project/branches/", {"branch_name": "main"})
        response_json = response.json()

        assert response.status_code == 200
        assert response_json["branch_name"] == "main"

    def test_get_file(self, client, encoded_filepath):
        response = client.get(f"/project/files/?filepath={encoded_filepath}")

        assert response.status_code == 200
        data = response.json()

        assert "{{ ref('stg_customers') }}" in data["contents"]

    def test_save_file(self, client, encoded_filepath):
        response = client.put(
            f"/project/files/?filepath={encoded_filepath}", {"contents": "test"}
        )

        assert response.status_code == 204

    def test_create_file(self, client):
        filepath = "models/marts/customer360/sales.sql"
        encoded_filepath = safe_encode(filepath)
        response = client.post(
            f"/project/files/?filepath={encoded_filepath}",
            {"contents": "salesly stuff"},
        )

        assert response.status_code == 201

    def test_create_file_with_directory(self, client):
        filepath = "models/marts/sales/funnel.sql"
        encoded_filepath = safe_encode(filepath)
        response = client.post(
            f"/project/files/?filepath={encoded_filepath}",
            {"contents": "salesly stuff"},
        )

        assert response.status_code == 201

    def test_delete_file(self, client, encoded_filepath):
        response = client.delete(f"/project/files/?filepath={encoded_filepath}")

        assert response.status_code == 204

    def test_delete_directory(self, client):
        filepath = "models/marts/"
        encoded_filepath = safe_encode(filepath)
        response = client.delete(f"/project/files/?filepath={encoded_filepath}")

        assert response.status_code == 204

    @pytest.mark.parametrize(
        "filepath_param,e2e",
        [
            ("models/marts/customer360/orders.sql", True),
            ("models/staging/stg_products.sql", False),
        ],
    )
    @pytest.mark.parametrize("branch_name", ["apple12345", "main"])
    def test_get_project_based_lineage_view(
        self, client, user, local_metabase, filepath_param, branch_name, e2e
    ):
        encoded_filepath = safe_encode(filepath_param)
        workspace = user.current_workspace()
        dbt_details = workspace.get_dbt_details()
        branch_id = uuid.uuid5(
            uuid.NAMESPACE_URL, f"{dbt_details.repository.git_repo_url}:{branch_name}"
        )
        Branch.objects.get_or_create(
            id=branch_id,
            workspace=workspace,
            repository=dbt_details.repository,
            branch_name=branch_name,
        )

        # get metabase assets
        db_read_path = "fixtures/datahub_dbs/metabase.duckdb"
        with open(db_read_path, "rb") as f:
            local_metabase.datahub_db.save(db_read_path, f, save=True)
        MetadataSyncWorkflow().process_metadata(
            ContextDebugger({"input": {"resource_id": local_metabase.id}})
        )
        assert_ingest_output(
            [local_metabase], containers=False, columns=False, column_links=False
        )

        # create metabase assets
        response = client.get(
            build_url(
                "/project/lineage/",
                {
                    "filepath": encoded_filepath,
                    "predecessor_depth": 1,
                    "successor_depth": 1,
                    "branch_id": branch_id,
                },
            )
        )
        assert response.status_code == 200
        lineage = response.json()["lineage"]
        assert lineage["asset_links"]
        assert lineage["column_links"]
        if e2e:
            source_target_combos = []
            asset_dict = {a["id"]: a for a in lineage["assets"]}
            for al in lineage["asset_links"]:
                source_asset = asset_dict[al["source_id"]]
                target_asset = asset_dict[al["target_id"]]
                if source_asset and target_asset:
                    source_target_combos.append(
                        (source_asset["resource_id"], target_asset["resource_id"])
                    )
            assert any([stc[0] != stc[1] for stc in source_target_combos])

    @pytest.mark.parametrize("branch_name", ["apple12345", "main"])
    def test_stream_dbt_command(self, client, branch_name):
        response = client.post(
            build_url("/project/stream_dbt_command/", {"branch_name": branch_name}),
            {"command": "run"},
        )
        if branch_name != "main":
            assert response.status_code == 404
        else:
            out = ""
            for chunk in response.streaming_content:
                c = chunk.decode("utf-8")
                print(c)
                out += c
            assert response.status_code == 200
            assert out.endswith("\nTrue")
