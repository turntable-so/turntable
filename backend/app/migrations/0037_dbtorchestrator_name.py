# Generated by Django 5.0.6 on 2024-11-20 22:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0036_alter_storagesettings_applies_to"),
    ]

    operations = [
        migrations.AddField(
            model_name="dbtorchestrator",
            name="name",
            field=models.CharField(default="Job", max_length=255),
        ),
    ]