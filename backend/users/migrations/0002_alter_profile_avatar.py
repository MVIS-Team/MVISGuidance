# Generated by Django 4.1.3 on 2023-03-28 10:02

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="profile",
            name="avatar",
            field=models.ImageField(blank=True, upload_to="profile"),
        ),
    ]
