import os
from uuid import UUID

from django.core.management.base import BaseCommand
from django.db import transaction

from app.models import Asset, SSHKey, Repository, Workspace, Resource
from fixtures.local_env import (
    create_local_metabase,
    create_local_postgres,
    create_local_user,
    create_local_workspace,
    create_repository_n,
    create_ssh_key_n,
)
from workflows.metadata_sync import MetadataSyncWorkflow
from workflows.utils.debug import WorkflowDebugger


class Command(BaseCommand):
    help = "Seed data with inital user and workspace"

    def handle(self, *args, **kwargs):
        workspace = Workspace.objects.get(name="Parkers Vinyl Shop")
        ssh_key = SSHKey.objects.first()
        print(ssh_key.public_key)
        git_repo_url = "https://github.com/turntable-so/jaffle-shop"
        resource = Resource.objects.get(id=UUID("f84748d7-d1de-431c-8b0c-ece555525141"))

        return Repository.objects.create(
            main_branch_name="main",
            workspace=workspace,
            git_repo_url=git_repo_url,
            ssh_key=ssh_key,
        )
