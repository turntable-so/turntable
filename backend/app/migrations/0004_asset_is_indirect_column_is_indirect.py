# Generated by Django 5.0.6 on 2024-09-04 20:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0003_alter_ingesterror_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="asset",
            name="is_indirect",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="column",
            name="is_indirect",
            field=models.BooleanField(default=False),
        ),
    ]
