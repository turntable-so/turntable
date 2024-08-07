# Generated by Django 5.0.6 on 2024-07-15 18:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0009_resource_parent_resource"),
    ]

    operations = [
        migrations.AlterField(
            model_name="asset",
            name="type",
            field=models.CharField(
                choices=[
                    ("model", "Model"),
                    ("source", "Source"),
                    ("seed", "Seed"),
                    ("table", "Table"),
                    ("analysis", "Analysis"),
                    ("metric", "Metric"),
                    ("snapshot", "Snapshot"),
                    ("view", "View"),
                    ("chart", "Chart"),
                    ("dashboard", "Dashboard"),
                    ("dataset", "Dataset"),
                ],
                max_length=20,
            ),
        ),
    ]
