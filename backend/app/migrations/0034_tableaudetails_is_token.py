# Generated by Django 5.0.6 on 2024-11-20 23:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0033_rename_dbt_resource_dbtorchestrator_dbtresource_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="tableaudetails",
            name="is_token",
            field=models.BooleanField(default=False),
        ),
    ]
