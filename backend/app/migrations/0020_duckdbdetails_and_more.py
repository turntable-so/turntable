# Generated by Django 5.0.6 on 2024-08-01 23:37

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "app",
            "0019_rename_app_resourc_resourc_cf97f1_idx_app_resourc_resourc_4c9b2d_idx_and_more",
        ),
    ]

    operations = [
        migrations.CreateModel(
            name="DuckDBDetails",
            fields=[
                (
                    "dbdetails_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="app.dbdetails",
                    ),
                ),
                ("path", models.TextField()),
            ],
            options={
                "abstract": False,
                "base_manager_name": "objects",
            },
            bases=("app.dbdetails",),
        ),
        migrations.RemoveIndex(
            model_name="githubinstallation",
            name="app_githubi_tenant__f7e3ea_idx",
        ),
        migrations.RemoveIndex(
            model_name="sshkey",
            name="app_sshkey_tenant__cb75b8_idx",
        ),
        migrations.RemoveField(
            model_name="githubinstallation",
            name="tenant_id",
        ),
        migrations.RemoveField(
            model_name="githubinstallation",
            name="user_id",
        ),
        migrations.RemoveField(
            model_name="sshkey",
            name="tenant_id",
        ),
        migrations.AddField(
            model_name="githubinstallation",
            name="user",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="githubinstallation",
            name="workspace",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="app.workspace",
            ),
        ),
        migrations.AddField(
            model_name="sshkey",
            name="workspace",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="app.workspace",
            ),
        ),
        migrations.AlterField(
            model_name="dbtcoredetails",
            name="github_repo_id",
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name="githubinstallation",
            name="id",
            field=models.CharField(
                default=uuid.uuid4, max_length=255, primary_key=True, serialize=False
            ),
        ),
        migrations.AlterField(
            model_name="lookerdetails",
            name="github_repo_id",
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name="resourcedetails",
            name="subtype",
            field=models.CharField(
                choices=[
                    ("looker", "Looker"),
                    ("metabase", "Metabase"),
                    ("bigquery", "BigQuery"),
                    ("snowflake", "Snowflake"),
                    ("postgres", "Postgres"),
                    ("duckdb", "File"),
                    ("file", "File"),
                ],
                max_length=255,
            ),
        ),
        migrations.AddIndex(
            model_name="githubinstallation",
            index=models.Index(
                fields=["workspace_id"], name="app_githubi_workspa_890585_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="sshkey",
            index=models.Index(
                fields=["workspace_id"], name="app_sshkey_workspa_cacad8_idx"
            ),
        ),
    ]
