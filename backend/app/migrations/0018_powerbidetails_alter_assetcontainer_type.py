# Generated by Django 5.0.6 on 2024-10-17 17:07

import app.utils.fields
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0017_alter_branch_unique_together"),
    ]

    operations = [
        migrations.CreateModel(
            name="PowerBIDetails",
            fields=[
                (
                    "resourcedetails_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="app.resourcedetails",
                    ),
                ),
                ("subtype", models.CharField(default="powerbi", max_length=255)),
                (
                    "client_id",
                    app.utils.fields.encrypt(models.CharField(max_length=255)),
                ),
                (
                    "client_secret",
                    app.utils.fields.encrypt(models.CharField(max_length=255)),
                ),
                (
                    "powerbi_workspace_id",
                    app.utils.fields.encrypt(models.CharField(max_length=255)),
                ),
                (
                    "powerbi_tenant_id",
                    app.utils.fields.encrypt(models.CharField(max_length=255)),
                ),
            ],
            options={
                "abstract": False,
                "base_manager_name": "objects",
            },
            bases=("app.resourcedetails",),
        ),
        migrations.AlterField(
            model_name="assetcontainer",
            name="type",
            field=models.CharField(
                choices=[
                    ("workbook", "Workbook"),
                    ("project", "Project"),
                    ("database", "Database"),
                    ("schema", "Schema"),
                    ("workspace", "Workspace"),
                ],
                max_length=255,
            ),
        ),
    ]
