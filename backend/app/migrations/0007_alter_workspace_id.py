# Generated by Django 5.0.6 on 2024-09-08 18:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0006_user_active_workspace"),
    ]

    operations = [
        migrations.AlterField(
            model_name="workspace",
            name="id",
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
