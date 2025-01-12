# Generated by Django 3.2.16 on 2022-10-28 16:08

from django.db import migrations, models
import signals.apps.signals.models.utils


class Migration(migrations.Migration):

    dependencies = [
        ('signals', '0163_category_icon'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='icon',
            field=models.FileField(blank=True, max_length=255, null=True, upload_to=signals.apps.signals.models.utils.upload_category_icon_to, validators=[signals.apps.signals.models.utils.validate_category_icon]),
        ),
    ]
