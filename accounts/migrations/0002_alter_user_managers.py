# Generated by Django 4.2.7 on 2025-07-11 14:32

import accounts.models
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelManagers(
            name="user",
            managers=[
                ("objects", accounts.models.CustomUserManager()),
            ],
        ),
    ]
