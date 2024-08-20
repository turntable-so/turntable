import json
import os

from django.core.management.base import BaseCommand

from app.models import (
    BigqueryDetails,
    DBTCoreDetails,
    GithubInstallation,
    Resource,
    ResourceType,
    User,
    Workspace,
)
from vinyl.lib.dbt_methods import DBTVersion


class Command(BaseCommand):
    help = "Seed data with inital user and workspace"

    def handle(self, *args, **kwargs):
        if User.objects.exists() or Workspace.objects.exists():
            self.stdout.write(
                self.style.WARNING("Data already exists. Skipping seeding.")
            )
            return

        user = User.objects.create_user(
            name="Turntable Dev", email="dev@turntable.so", password="OauthToken"
        )
        # create turntable full
        workspace = Workspace.objects.create(
            id="org_2XVt0EheumDcoCerhQzcUlVmXvG",
            name="Parkers Vinyl Shop",
        )
        # this bootstraps the necessary conditions
        workspace.add_admin(user)
        workspace.save()
        github_installation = GithubInstallation.objects.create(
            id=50270427,
            workspace=workspace,
            user=user,
        )
        github_installation2 = GithubInstallation.objects.create(
            id=51092020, workspace=workspace, user=user
        )
        bigquery_resource = Resource.objects.create(
            type=ResourceType.DB,
            workspace=workspace,
        )
        if gac := os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
            BigqueryDetails(
                resource=bigquery_resource,
                lookback_days=1,
                schema_include=["analytics", "analytics-mini"],
                service_account=json.loads(gac.replace("\n", "\\n")),
            ).save()
            DBTCoreDetails(
                resource=bigquery_resource,
                github_installation=github_installation,
                github_repo_id="599220755",
                project_path=".",
                threads=6,
                database="analytics-dev-372514",
                version=DBTVersion.V1_5.value,
                schema="analytics",
            ).save()
            DBTCoreDetails(
                resource=bigquery_resource,
                github_installation=github_installation2,
                github_repo_id="804953758",
                project_path=".",
                threads=6,
                database="analytics-dev-372514",
                version=DBTVersion.V1_7.value,
                schema="analytics_mini",
            ).save()

        self.stdout.write(self.style.SUCCESS("Successfully seeded the database"))
