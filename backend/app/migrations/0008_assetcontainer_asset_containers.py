# Generated by Django 5.0.6 on 2024-09-07 20:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0007_tableaudetails"),
    ]

    operations = [
        migrations.CreateModel(
            name="AssetContainer",
            fields=[
                (
                    "id",
                    models.TextField(editable=False, primary_key=True, serialize=False),
                ),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("workbook", "Workbook"),
                            ("project", "Project"),
                            ("database", "Database"),
                            ("schema", "Schema"),
                        ],
                        max_length=255,
                    ),
                ),
                ("name", models.TextField()),
                ("description", models.TextField(null=True)),
                (
                    "workspace",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="app.workspace",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="asset",
            name="containers",
            field=models.ManyToManyField(
                related_name="assets", to="app.assetcontainer"
            ),
        ),
    ]