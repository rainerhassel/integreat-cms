"""
Make title for push notification translations optional
"""

# Generated by Django 3.2.15 on 2022-09-23 12:48

from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Make title for push notification translations optional
    """

    dependencies = [
        ("cms", "0041_region_hix_enabled"),
    ]

    operations = [
        migrations.AlterField(
            model_name="pushnotificationtranslation",
            name="title",
            field=models.CharField(blank=True, max_length=250, verbose_name="title"),
        ),
    ]
