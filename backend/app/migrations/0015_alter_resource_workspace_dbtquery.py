# Generated by Django 5.0.6 on 2024-09-30 18:55

import uuid

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models

import app.services.storage_backends


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0014_workspace_assets_exclude_name_contains"),
    ]

    operations = [
        migrations.AlterField(
            model_name="resource",
            name="workspace",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="resources",
                to="app.workspace",
            ),
        ),
        migrations.CreateModel(
            name="DBTQuery",
            fields=[
                ("user_id", models.CharField(max_length=255)),
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(auto_now=True, null=True)),
                ("dbt_sql", models.TextField(null=True)),
                (
                    "results",
                    models.FileField(
                        null=True,
                        storage=app.services.storage_backends.CustomS3Boto3StorageDeprecated(),
                        upload_to="dbt_query_results/",
                    ),
                ),
                (
                    "dbtresource",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="app.dbtresource",
                    ),
                ),
                (
                    "workspace",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="app.workspace"
                    ),
                ),
            ],
        ),
    ]
