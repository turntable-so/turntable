# Generated by Django 5.0.6 on 2024-11-07 23:18

import app.utils.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0024_merge_20241106_2149"),
    ]

    operations = [
        migrations.AddField(
            model_name="workspace",
            name="anthropic_api_key",
            field=app.utils.fields.encrypt(
                models.CharField(blank=True, max_length=255, null=True)
            ),
        ),
        migrations.AddField(
            model_name="workspace",
            name="openai_api_key",
            field=app.utils.fields.encrypt(
                models.CharField(blank=True, max_length=255, null=True)
            ),
        ),
    ]
