# Generated by Django 5.0.6 on 2024-09-06 17:55

import app.utils.fields
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0004_asset_is_indirect_column_is_indirect"),
    ]

    operations = [
        migrations.CreateModel(
            name="DatabricksDetails",
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
                ("subtype", models.CharField(default="databricks", max_length=255)),
                ("host", app.utils.fields.encrypt(models.CharField(max_length=255))),
                ("token", app.utils.fields.encrypt(models.CharField(max_length=255))),
                (
                    "http_path",
                    app.utils.fields.encrypt(models.CharField(max_length=255)),
                ),
            ],
            options={
                "abstract": False,
                "base_manager_name": "objects",
            },
            bases=("app.dbdetails",),
        ),
    ]
