# Generated by Django 2.1.7 on 2019-06-07 12:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('signals', '0060_statusmessagetemplate_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='statusmessagetemplate',
            name='title',
            field=models.CharField(max_length=255),
        ),
    ]