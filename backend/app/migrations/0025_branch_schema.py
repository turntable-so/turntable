# Generated by Django 5.0.6 on 2024-11-07 20:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0024_merge_20241106_2149"),
    ]

    operations = [
        migrations.AddField(
            model_name="branch",
            name="schema",
            field=models.CharField(max_length=255, null=True),
        ),
    ]