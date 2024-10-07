# Generated by Django 4.2.13 on 2024-08-20 16:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Make the fields "title" and "name" not mandatory.
    Rename the field from "poi" to "location".
    """

    dependencies = [
        ("cms", "0105_treebeard_models_add_deferrable_tree_constraints"),
    ]

    operations = [
        migrations.AlterField(
            model_name="contact",
            name="title",
            field=models.CharField(blank=True, max_length=200, verbose_name="title"),
        ),
        migrations.AlterField(
            model_name="contact",
            name="name",
            field=models.CharField(blank=True, max_length=200, verbose_name="name"),
        ),
        migrations.RenameField(
            model_name="contact",
            old_name="poi",
            new_name="location",
        ),
        migrations.AlterField(
            model_name="contact",
            name="location",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="contacts",
                to="cms.poi",
                verbose_name="location",
            ),
        ),
        migrations.AddConstraint(
            model_name="contact",
            constraint=models.UniqueConstraint(
                models.F("location"),
                condition=models.Q(("title", "")),
                name="contact_singular_empty_title_per_location",
                violation_error_message="Only one contact per location can have an empty title.",
            ),
        ),
        migrations.AddConstraint(
            model_name="contact",
            constraint=models.CheckConstraint(
                check=models.Q(
                    models.Q(("title", ""), _negated=True),
                    models.Q(("name", ""), _negated=True),
                    models.Q(("email", ""), _negated=True),
                    models.Q(("phone_number", ""), _negated=True),
                    models.Q(("website", ""), _negated=True),
                    _connector="OR",
                ),
                name="contact_non_empty",
                violation_error_message="One of the following fields must be filled: title, name, e-mail, phone number, website.",
            ),
        ),
    ]
