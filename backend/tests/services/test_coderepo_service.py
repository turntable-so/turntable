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
from vinyl.lib.dbt_methods import DBTVersion


@pytest.mark.django_db
class CodeRepoServiceTests(TestCase):

    git_repo_url = "git@github.com:turntable-so/jaffle-shop.git"
    # test keys, not used in production
    test_ssh_public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDfjTM6KSLm6fVYjLNYosPupbjDwavf6thtHje+pBg0QLgn9hR2W0kiHRoomMIc8OBVoYk8xzQOQDGlx4uoobdQwiONwEqAzdisKVsZSW1mejuBWpxxkzTQx3rVtAmy3bSspiGIqwFWbKAiWoHTvSq6XXriHrs4iZX1f9cnp6AE0FdG3xWYpYlC3wmeK010F/9U2RVYTMikUyPj8CPmNmH0E00f00Nlk43EjwITpcNt5nzzL8Mvet7c2Bh4udp2WVItnK0Jh4G1yYxKg7835vcRzVRwJiARbA9i7+9fzmHZHWEJucSw04M98pPdWyokBHpdRj8hBTXgjh5+wN92SVwL"
    test_ssh_private_key = "-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEA340zOiki5un1WIyzWKLD7qW4w8Gr3+rYbR43vqQYNEC4J/YU\ndltJIh0aKJjCHPDgVaGJPMc0DkAxpceLqKG3UMIjjcBKgM3YrClbGUltZno7gVqc\ncZM00Md61bQJst20rKYhiKsBVmygIlqB070qul164h67OImV9X/XJ6egBNBXRt8V\nmKWJQt8JnitNdBf/VNkVWEzIpFMj4/Aj5jZh9BNNH9NDZZONxI8CE6XDbeZ88y/D\nL3re3NgYeLnadllSLZytCYeBtcmMSoO/N+b3Ec1UcCYgEWwPYu/vX85h2R1hCbnE\nsNODPfKT3VsqJAR6XUY/IQU14I4efsDfdklcCwIDAQABAoIBADvf5LWSKP/x772M\nychWp+W2SztbFv69NsRbEJEmADmWj/xcA3UD1B2n78apy2vW9C7bOhemPwIGHYYK\nYRSEY8XkiYNA2nOPLpZF6Vlnej61RFTMARTGWaIFm5e7RdG7YdXQFTE2pAASzf0F\ngrpEczpBKVWA56In75s2Z1j+o3RGHIgBjnuVC1pK0JV+84jvaV5SWTHGWqqxGLnP\nQNtDKqGeNvmrrYq1u/f9K+tQRl5MJw14NlI+NluQaTgfcG8wE/BlGqCjALUiZLh4\nqEwNKs7Eh2b0qJjUJGvpiITdzJ1qzF7VaZWpWKqW7ws+vujn7hf+exAkgI1UBvY9\nS9W0JpkCgYEA/i/FX2AxyUuOJ/huly4fnI5dEKNQGNIj06xwga7JdsEXAUceMHvB\nzwL9eRwg0dKW6mQqc2z3gGvdb5CsKbC1C0UQ87tUMUf5XIknakQ3Uai8DiolpnUl\nUOgq2T9s7zRm/0atSFE/upUhhbfbAo/xXIn+8DG43KGZiHNJN5J+nn8CgYEA4SV6\nuFkKZKI2qRWmaXk4etfueCBKhG6IdjIpNhwBpusK/Rtka0ZLg9bUnCreP6sryrbR\nVfdUgB62P12ugSyKsbA/10P/K3/PFIr0kTRNhjrb85KkWhYiAJcBhJU56sWflu1r\nbJeJ5AzE9J8FWgfrwNJZ8kVd/FEL1FS03Y93FHUCgYEAj6wKwJ0Lpv6YzEjkoXkF\njyT8v3G/zTfB3lwif3p/DyuWyDcdfkQFSPAkuzbF6jNA8B1LzVAzGRhe4jeAyFPE\nESmpqkohDXXkIYS4jZ0fM33PRaZW/55JSFDiH0d1WENjUDjvqueZwOmYOA+yr+ES\niL7LJZLFLZf9wx1+rfWUshsCgYAXorefYrmUlvLmDT/LEs67FrASLFGmVXQ99EYf\nSBFkVIhyyc1g9aA31vW670UlqfKO9WJEhBJ64L6BKHSJWwO0Y6xQDPNcva4fmfbS\nx4rb7JHqoBpg2rH3HeMq5/+MhfKbBZGhdMclCbIjfA4zxWEafPq0VFPpiRiU0c+q\n8sStgQKBgQCNnh+y4QppC8UW8irxjZHNCuv+CUlHOjHhm82WHUm1flvDtIxHW3S8\nUKyhS4c9AgIywA7DXxSize7HpSZb3DqWg0DIq7FnRuHykLqPF0PiCMCi1sGWfp31\nMMLk7skCAIkXKyclGYQamgtuj87I13ZHnZYM4DwYgiklLXf8F5J4qw==\n-----END RSA PRIVATE KEY-----\n"

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
            public_key=self.test_ssh_public_key,
            private_key=self.test_ssh_private_key,
        )

        data = {
            "public_key": self.test_ssh_public_key,
            "git_repo_url": self.git_repo_url,
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
            public_key=self.test_ssh_public_key,
            private_key=self.test_ssh_private_key,
        )
        data = {
            "public_key": self.test_ssh_public_key,
            "git_repo_url": self.git_repo_url,
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
            public_key=self.test_ssh_public_key,
            private_key=self.test_ssh_private_key,
        )
        data = {
            "public_key": self.test_ssh_public_key,
            "git_repo_url": self.git_repo_url,
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
            git_repo_url=self.git_repo_url,
            resource=bigquery_resource,
            deploy_key=self.test_ssh_public_key,
            main_git_branch="main",
            project_path=".",
            threads=1,
            version=DBTVersion.V1_6,
            database="test",
            schema="test",
        )
        with details.dbt_repo_context() as (project, filepath):
            assert project != None
            assert filepath != None
