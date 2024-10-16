from urllib.parse import quote, unquote

import pytest

from app.utils.test_utils import require_env_vars


def safe_encode(s):
    return quote(s, safe="")


def safe_decode(s):
    return unquote(s)


@pytest.mark.django_db
@pytest.mark.usefixtures("force_isolate", "local_postgres")
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
        breakpoint()
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
        "filepath_param",
        [
            "models/marts/customer360/customers.sql",
            "models/staging/stg_products.sql",
        ],
    )
    def test_get_project_based_lineage_view(self, client, filepath_param):
        encoded_filepath = safe_encode(filepath_param)
        response = client.get(
            "/project/lineage/",
            {
                "filepath": encoded_filepath,
                "predecessor_depth": 1,
                "successor_depth": 1,
            },
        )
        assert response.status_code == 200
        for asset in response.json()["lineage"]["assets"]:
            assert len(asset["columns"]) > 0

        assert response.json()["lineage"]["asset_links"]
        assert response.json()["lineage"]["column_links"]
