# SPDX-License-Identifier: MPL-2.0
# Copyright (C) 2018 - 2021 Gemeente Amsterdam
from django.db import migrations
from django.utils.text import slugify


def create_new_categories(apps, schema_editor):
    pass


def remove_new_categories(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    """
    SIG-858 [BE] Nieuwe (sub)categorieen; Wegsleep

    This migration will add the new sub category "Wegsleep"

    Main category:
     - overlast-in-de-openbare-ruimte

    Sub category:
     - Wegsleep
    """
    dependencies = [
        ('signals', '0026_history'),
    ]

    operations = [
        migrations.RunPython(create_new_categories, remove_new_categories),
    ]
