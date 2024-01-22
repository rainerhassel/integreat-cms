# Generated by Django 3.2.20 on 2023-09-21 08:22

from __future__ import annotations

from typing import TYPE_CHECKING

from django.db import migrations, models

if TYPE_CHECKING:
    from django.apps.registry import Apps
    from django.db.backends.base.schema import BaseDatabaseSchemaEditor


# pylint: disable=unused-argument
def set_default_appointment_only(
    apps: Apps, schema_editor: BaseDatabaseSchemaEditor
) -> None:
    """
    Set default value for appointmentOnly

    :param apps: The configuration of installed applications
    :param schema_editor: The database abstraction layer that creates actual SQL code
    """
    POI = apps.get_model("cms", "POI")
    for obj in POI.objects.all():
        for item in obj.opening_hours:
            item["appointmentOnly"] = False
        obj.save()


class Migration(migrations.Migration):
    """
    Add field for setting appointment link and
    set default appointment only opening hours for all existing POIs
    """

    dependencies = [
        ("cms", "0080_alter_poi_category"),
    ]

    operations = [
        migrations.AddField(
            model_name="poi",
            name="appointment_url",
            field=models.URLField(
                blank=True,
                help_text="Link to an external website where an appointment for this location can be made.",
                max_length=500,
                verbose_name="appointment link",
            ),
        ),
        migrations.RunPython(set_default_appointment_only),
    ]