# Generated by Django 5.0.6 on 2024-08-02 22:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0020_duckdbdetails_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="assetlink",
            name="id",
            field=models.TextField(editable=False, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name="columnlink",
            name="id",
            field=models.TextField(editable=False, primary_key=True, serialize=False),
        ),
    ]