import os
from urllib.parse import quote, unquote

import pytest

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
    def branch(self, local_postgres):
        return local_postgres.get_dbt_resource().repository.main_branch

    def test_clone(self, client, branch):
        response = client.post(f"/project/{branch.id}/clone/")
        assert response.status_code == 204

    def test_file_index(self, client, branch):
        response = client.get(f"/project/{branch.id}/files/")
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

    def test_get_file(self, client, branch, encoded_filepath):
        response = client.get(
            f"/project/{branch.id}/files/?filepath={encoded_filepath}"
        )

        assert response.status_code == 200
        data = response.json()

        assert "{{ ref('stg_customers') }}" in data["contents"]

    def test_save_file(self, client, branch, encoded_filepath):
        response = client.put(
            f"/project/{branch.id}/files/?filepath={encoded_filepath}",
            {"contents": "test"},
        )

        assert response.status_code == 204

    def test_create_file(self, client, branch):
        filepath = "models/marts/customer360/sales.sql"
        encoded_filepath = safe_encode(filepath)
        response = client.post(
            f"/project/{branch.id}/files/?filepath={encoded_filepath}",
            {"contents": "salesly stuff"},
        )

        assert response.status_code == 201

    def test_create_file_with_directory(self, client, branch):
        filepath = "models/marts/sales/funnel.sql"
        encoded_filepath = safe_encode(filepath)
        response = client.post(
            f"/project/{branch.id}/files/?filepath={encoded_filepath}",
            {"contents": "salesly stuff"},
        )

        assert response.status_code == 201

    def test_delete_file(self, client, branch, encoded_filepath):
        response = client.delete(
            f"/project/{branch.id}/files/?filepath={encoded_filepath}"
        )

        assert response.status_code == 204

    def test_delete_directory(self, client, branch):
        filepath = "models/marts/"
        encoded_filepath = safe_encode(filepath)
        response = client.delete(
            f"/project/{branch.id}/files/?filepath={encoded_filepath}"
        )

        assert response.status_code == 204

    @pytest.mark.parametrize(
        "filepath_param",
        [
            "models/marts/customer360/customers.sql",
            "models/staging/stg_products.sql",
        ],
    )
    def test_get_project_based_lineage_view(self, client, branch, filepath_param):
        encoded_filepath = safe_encode(filepath_param)
        response = client.get(
            build_url(
                f"/project/{branch.id}/lineage/",
                {
                    "filepath": encoded_filepath,
                    "predecessor_depth": 1,
                    "successor_depth": 1,
                },
            )
        )
        assert response.status_code == 200
        assert len(response.json()["lineage"]["asset_links"]) > 0
        assert len(response.json()["lineage"]["column_links"]) > 0


@pytest.mark.django_db
@pytest.mark.usefixtures("local_postgres")
@require_env_vars("SSHKEY_0_PUBLIC", "SSHKEY_0_PRIVATE")
class TestFileChanges:

    @pytest.fixture
    def branch(self, local_postgres):
        return local_postgres.get_dbt_resource().repository.main_branch

    def test_file_changes(self, client, branch):
        # edit use case
        result = client.put(
            f"/project/{branch.id}/files/?filepath={safe_encode('models/marts/customer360/customers.sql')}",
            {"contents": "modified customers content"},
        )

        # new file use case
        client.post(
            f"/project/{branch.id}/files/?filepath={safe_encode('models/marts/customer360/sales.sql')}",
            {"contents": "a bunch of sales sql"},
        )
        response = client.get(f"/project/{branch.id}/changes/")
        assert response.status_code == 200
        assert len(response.json()["untracked"]) == 1
        assert len(response.json()["modified"]) == 1
