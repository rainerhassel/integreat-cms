# Generated by Django 4.2.13 on 2024-06-11 07:49

from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Add a default value for language colors
    """

    dependencies = [
        ("cms", "0093_add_language_color"),
    ]

    operations = [
        migrations.AlterField(
            model_name="language",
            name="language_color",
            field=models.CharField(
                choices=[
                    ("#FFBB78", "Mellow apricot"),
                    ("#2CA02C", "Forest green"),
                    ("#FF9896", "Rose"),
                    ("#C5B0D5", "Tropical violet"),
                    ("#FF4500", "Red"),
                    ("#FFA500", "Orange"),
                    ("#17157D", "Dark blue"),
                    ("#1F77B4", "Green blue"),
                    ("#FFD700", "Yellow"),
                    ("#008080", "Teal"),
                    ("#9EDAE5", "Arctic"),
                    ("#5894E3", "Azure"),
                    ("#17BECF", "Pacific blue"),
                    ("#FF6347", "Orange red"),
                    ("#98DF8A", "Light green"),
                    ("#9467BD", "Violet"),
                    ("#ADFF2F", "Lime"),
                    ("#E377C2", "Lavender"),
                    ("#8C564B", "Brown"),
                    ("#FFA07A", "Pink orange"),
                    ("#FFE4F0", "Pastel pink"),
                    ("#F0E68C", "Khaki"),
                    ("#BCBD22", "Yellow green"),
                    ("#800080", "Mauve"),
                    ("#BA55D3", "Purple"),
                    ("#DBDB8D", "Primrose"),
                    ("#4B5563", "Fiord"),
                    ("#C49C94", "Quicksand"),
                    ("#7F7F7F", "Grey"),
                    ("#26FCFF", "Aqua"),
                    ("#20B2AA", "Pine green"),
                    ("#FFDAB9", "Almond"),
                    ("#D62728", "Cherry"),
                ],
                default="#000000",
                help_text="This color is used to represent the color label of the chosen language",
                max_length=7,
                verbose_name="language color",
            ),
        ),
    ]
