# Generated by Django 5.1.3 on 2024-11-21 22:54

import uuid

import django.contrib.postgres.fields
import django.db.models.deletion
from django.db import migrations, models

import app.models.resources
import app.models.workflows
import app.services.storage_backends
import app.utils.fields


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0034_tableaudetails_is_token"),
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        migrations.CreateModel(
            name="WorkspaceSettings",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "polymorphic_ctype",
                    models.ForeignKey(
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="polymorphic_%(app_label)s.%(class)s_set+",
                        to="contenttypes.contenttype",
                    ),
                ),
                (
                    "workspace",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="app.workspace"
                    ),
                ),
            ],
            options={
                "abstract": False,
                "base_manager_name": "objects",
            },
        ),
        migrations.AlterField(
            model_name="block",
            name="results",
            field=app.services.storage_backends.CustomFileField(
                null=True, storage_category="data", upload_to="results/"
            ),
        ),
        migrations.AlterField(
            model_name="dbtquery",
            name="results",
            field=app.services.storage_backends.CustomFileField(
                null=True, storage_category="data", upload_to="dbt_query_results/"
            ),
        ),
        migrations.AlterField(
            model_name="dbtresource",
            name="catalog",
            field=app.services.storage_backends.CustomFileField(
                null=True,
                storage_category="metadata",
                upload_to=app.models.resources.DBTResource.custom_metadata_upload_to,
            ),
        ),
        migrations.AlterField(
            model_name="dbtresource",
            name="manifest",
            field=app.services.storage_backends.CustomFileField(
                null=True,
                storage_category="metadata",
                upload_to=app.models.resources.DBTResource.custom_metadata_upload_to,
            ),
        ),
        migrations.AlterField(
            model_name="query",
            name="results",
            field=app.services.storage_backends.CustomFileField(
                null=True, storage_category="data", upload_to="query_results/"
            ),
        ),
        migrations.AlterField(
            model_name="resource",
            name="datahub_db",
            field=app.services.storage_backends.CustomFileField(
                null=True, storage_category="metadata", upload_to="datahub_dbs/"
            ),
        ),
        migrations.AlterField(
            model_name="taskartifact",
            name="artifact",
            field=app.services.storage_backends.CustomFileField(
                storage_category="metadata",
                upload_to=app.models.workflows.TaskArtifact.custom_upload_to,
            ),
        ),
        migrations.CreateModel(
            name="StorageSettings",
            fields=[
                (
                    "workspacesettings_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="app.workspacesettings",
                    ),
                ),
                (
                    "applies_to",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(
                            choices=[("data", "Data"), ("metadata", "Metadata")],
                            max_length=255,
                        ),
                        default=["data", "metadata"],
                        null=True,
                        size=None,
                    ),
                ),
                (
                    "s3_access_key",
                    app.utils.fields.encrypt(models.CharField(max_length=255)),
                ),
                (
                    "s3_secret_key",
                    app.utils.fields.encrypt(models.CharField(max_length=255)),
                ),
                ("s3_endpoint_url", models.URLField(max_length=2000)),
                (
                    "s3_public_url",
                    models.URLField(blank=True, max_length=2000, null=True),
                ),
                ("s3_bucket_name", models.CharField(max_length=255)),
                (
                    "s3_region_name",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
            ],
            options={
                "abstract": False,
                "base_manager_name": "objects",
            },
            bases=("app.workspacesettings",),
        ),
    ]
