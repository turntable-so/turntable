# Generated by Django 5.0.6 on 2024-09-07 20:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0008_assetcontainer_asset_containers"),
    ]

    operations = [
        migrations.AlterField(
            model_name="asset",
            name="id",
            field=models.CharField(
                editable=False, max_length=255, primary_key=True, serialize=False
            ),
        ),
        migrations.AlterField(
            model_name="assetcontainer",
            name="id",
            field=models.CharField(
                editable=False, max_length=255, primary_key=True, serialize=False
            ),
        ),
        migrations.AlterField(
            model_name="assetlink",
            name="id",
            field=models.CharField(
                editable=False, max_length=255, primary_key=True, serialize=False
            ),
        ),
        migrations.AlterField(
            model_name="column",
            name="id",
            field=models.CharField(
                editable=False, max_length=255, primary_key=True, serialize=False
            ),
        ),
        migrations.AlterField(
            model_name="columnlink",
            name="id",
            field=models.CharField(
                editable=False, max_length=255, primary_key=True, serialize=False
            ),
        ),
    ]