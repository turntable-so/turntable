import os
from urllib.parse import quote, unquote

import pytest

from app.models.resources import DBTCoreDetails
from app.utils.test_utils import require_env_vars
from app.utils.url import build_url


def safe_encode(s):
    return quote(s, safe="")


def safe_decode(s):
    return unquote(s)


@pytest.mark.django_db
@pytest.mark.usefixtures("force_isolate", "local_postgres")
class TestProjectViews:
    @pytest.fixture
    def encoded_filepath(self):
        return safe_encode("models/marts/customer360/customers.sql")

    @pytest.fixture
    def project(self, local_postgres):
        return DBTCoreDetails.get_development_dbtresource(
            workspace_id=local_postgres.workspace.id,
            resource_id=local_postgres.id,
        ).repository.main_project

    def test_clone(self, client, project):
        response = client.post(f"/project/{project.id}/clone/")
        assert response.status_code == 204

    def test_file_index(self, client, project):
        response = client.get(f"/project/{project.id}/files/")
        response_json = response.json()

        assert response.status_code == 200
        assert len(response_json["file_index"]) > 0

    def test_create_project_branch(self, client):
        random_hex = "".join([hex(x)[2:] for x in os.urandom(32)])
        response = client.post(
            "/project/branches/",
            {
                "branch_name": "test" + random_hex,
                "source_branch": "main",
                "schema": "test",
            },
        )
        assert response.status_code == 201

    def test_list_project_branches(self, client):
        response = client.get("/project/branches/")
        branches = response.json()

        assert response.status_code == 200
        assert branches["main_remote_branch"] == "main"
        assert len(branches["remote_branches"]) > 0

    def test_list_projects(self, client):
        response = client.get("/project/")
        projects = response.json()

        assert response.status_code == 200
        assert len(projects) > 0

    def test_get_file(self, client, project, encoded_filepath):
        response = client.get(
            f"/project/{project.id}/files/?filepath={encoded_filepath}"
        )

        assert response.status_code == 200
        data = response.json()

        assert "{{ ref('stg_customers') }}" in data["contents"]

    def test_save_file(self, client, project, encoded_filepath):
        response = client.put(
            f"/project/{project.id}/files/?filepath={encoded_filepath}",
            {"contents": "test"},
        )

        assert response.status_code == 200

    def test_create_file(self, client, project):
        filepath = "models/marts/customer360/sales.sql"
        encoded_filepath = safe_encode(filepath)
        response = client.post(
            f"/project/{project.id}/files/?filepath={encoded_filepath}",
            {"contents": "salesly stuff"},
        )

        assert response.status_code == 201

    def test_change_file_path(self, client, project):
        filepath = "models/marts/customer360/orders.sql"
        encoded_filepath = safe_encode(filepath)
        response = client.get(
            f"/project/{project.id}/files/?filepath={encoded_filepath}"
        )
        assert response.status_code == 200

        response = client.patch(
            f"/project/{project.id}/files/?filepath={encoded_filepath}",
            {"new_path": "models/marts/customer360/new_orders.sql"},
        )
        assert response.status_code == 204

    def test_create_file_with_directory(self, client, project):
        filepath = "models/marts/sales/funnel.sql"
        encoded_filepath = safe_encode(filepath)
        response = client.post(
            f"/project/{project.id}/files/?filepath={encoded_filepath}",
            {"contents": "salesly stuff"},
        )

        assert response.status_code == 201

    def test_delete_file(self, client, project, encoded_filepath):
        response = client.delete(
            f"/project/{project.id}/files/?filepath={encoded_filepath}"
        )

        assert response.status_code == 204

    def test_delete_directory(self, client, project):
        filepath = "models/marts/"
        encoded_filepath = safe_encode(filepath)
        response = client.delete(
            f"/project/{project.id}/files/?filepath={encoded_filepath}"
        )

        assert response.status_code == 204

    @pytest.mark.parametrize(
        "filepath_param",
        [
            "models/marts/customer360/customers.sql",
            "models/staging/stg_products.sql",
        ],
    )
    @pytest.mark.parametrize("asset_only", [True, False])
    def test_get_project_based_lineage_view(
        self, client, project, filepath_param, asset_only
    ):
        encoded_filepath = safe_encode(filepath_param)
        response = client.get(
            build_url(
                f"/project/{project.id}/lineage/",
                {
                    "filepath": encoded_filepath,
                    "predecessor_depth": 1,
                    "successor_depth": 1,
                    "asset_only": asset_only,
                },
            )
        )
        assert response.status_code == 200

        lineage_out = response.json()["lineage"]
        assert len(lineage_out["asset_links"]) > 0
        if not asset_only:
            assert len(lineage_out["column_links"]) > 0

    def test_compile_query(self, client, project):
        response = client.post(
            f"/project/{project.id}/compile/",
            {"filepath": safe_encode("models/marts/customer360/customers.sql")},
        )
        assert response.status_code == 200
        assert 'select * from "mydb"' in response.json()

    def test_duplicate_file(self, client, project):
        response = client.post(
            f"/project/{project.id}/files/duplicate/",
            {"filepath": safe_encode("models/marts/customer360/customers.sql")},
        )
        assert response.status_code == 200

    def test_duplicate_folder(self, client, project):
        response = client.post(
            f"/project/{project.id}/files/duplicate/",
            {"filepath": safe_encode("models/marts/customer360")},
        )
        assert response.status_code == 200


@pytest.mark.django_db
@pytest.mark.usefixtures("local_postgres")
@require_env_vars("SSHKEY_0_PUBLIC", "SSHKEY_0_PRIVATE")
class TestFileChanges:
    @pytest.fixture
    def project(self, local_postgres):
        return DBTCoreDetails.get_development_dbtresource(
            workspace_id=local_postgres.workspace.id,
            resource_id=local_postgres.id,
        ).repository.main_project

    def test_file_changes(self, client, project):
        # edit use case
        result = client.put(
            f"/project/{project.id}/files/?filepath={safe_encode('models/marts/customer360/customers.sql')}",
            {"contents": "modified customers content"},
        )

        # new file use case
        client.post(
            f"/project/{project.id}/files/?filepath={safe_encode('models/marts/customer360/sales.sql')}",
            {"contents": "a bunch of sales sql"},
        )
        response = client.get(f"/project/{project.id}/changes/")
        assert response.status_code == 200
        assert len(response.json()["untracked"]) == 1
        assert len(response.json()["modified"]) == 1
