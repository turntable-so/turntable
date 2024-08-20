import json
import os

import pytest
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from app.models import User, Workspace
from app.models.git_connections import SSHKey
from app.models.resources import BigqueryDetails, DBTCoreDetails, Resource, ResourceType
from app.services.code_repo_service import CodeRepoService

User = get_user_model()


@pytest.mark.django_db
class CodeRepoServiceTests(TestCase):

    def setUp(self):
        # Set up initial data
        self.user = User.objects.create_user(
            email="testuser@test.com", password="password"
        )
        self.workspace = Workspace.objects.create(name="Test workspace")
        self.workspace.users.add(self.user)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_repo_connection(self):

        SSHKey.objects.create(
            workspace_id=self.workspace.id,
            public_key=ssh_key,
            private_key=private_key,
        )

        data = {
            "public_key": ssh_key,
            "git_repo_url": git_repo_url,
        }

        coderepo_service = CodeRepoService(workspace_id=self.workspace.id)
        res = coderepo_service.test_repo_connection(
            public_key=data.get("public_key"),
            git_repo_url=data.get("git_repo_url"),
        )
        assert res["success"] == True

    def test_repo_context(self):

        SSHKey.objects.create(
            workspace_id=self.workspace.id,
            public_key=ssh_key,
            private_key=private_key,
        )
        data = {
            "public_key": ssh_key,
            "git_repo_url": git_repo_url,
        }
        coderepo_service = CodeRepoService(workspace_id=self.workspace.id)
        with coderepo_service.repo_context(
            public_key=data.get("public_key"),
            git_repo_url=data.get("git_repo_url"),
        ) as repo:
            assert len(os.listdir(repo)) > 3

    def test_dbt_repo_context(self):
        SSHKey.objects.create(
            workspace_id=self.workspace.id,
            public_key=ssh_key,
            private_key=private_key,
        )
        data = {
            "public_key": ssh_key,
            "git_repo_url": git_repo_url,
        }
        bigquery_resource = Resource.objects.create(
            type=ResourceType.DB,
            workspace=self.workspace,
        )
        gac = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        BigqueryDetails(
            resource=bigquery_resource,
            lookback_days=1,
            schema_include=["analytics", "analytics-mini"],
            service_account=json.loads(gac.replace("\n", "\\n")),
        ).save()

        details = DBTCoreDetails.objects.create(
            git_repo_url=git_repo_url,
            resource=bigquery_resource,
            deploy_key=ssh_key,
            main_git_branch="main",
            project_path=".",
            threads=1,
            version="1.6",
            database="test",
            schema="test",
        )
        with details.dbt_repo_context() as (project, filepath):
            assert project != None
            assert filepath != None
