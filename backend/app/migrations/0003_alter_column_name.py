# Generated by Django 5.0.6 on 2024-07-09 18:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0002_assetembedding"),
    ]

    operations = [
        migrations.AlterField(
            model_name="column",
            name="name",
            field=models.CharField(),
        ),
    ]
