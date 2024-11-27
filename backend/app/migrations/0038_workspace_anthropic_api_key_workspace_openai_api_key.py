# Generated by Django 5.1.3 on 2024-11-26 21:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0037_dbtorchestrator_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="workspace",
            name="anthropic_api_key",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="workspace",
            name="openai_api_key",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
