# Generated by Django 2.2.12 on 2020-06-05 08:05

import django.contrib.postgres.fields.jsonb
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('signals', '0112_reporter_sharing_allowed'),
    ]

    operations = [
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=255)),
                ('field_type', models.CharField(choices=[('plain_text', 'PlainText'), ('text_input', 'TextInput'), ('multi_text_input', 'MultiTextInput'), ('checkbox_input', 'CheckboxInput'), ('radio_input', 'RadioInput'), ('select_input', 'SelectInput'), ('text_area_input', 'TextareaInput'), ('map_select', 'MapSelect')], default='plain_text', max_length=32)), # noqa
                ('meta', django.contrib.postgres.fields.jsonb.JSONField(null=True)),
                ('required', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name_plural': 'Questions',
            },
        ),
        migrations.CreateModel(
            name='CategoryQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(null=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='signals.Category')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='signals.Question')),
            ],
        ),
        migrations.AddField(
            model_name='category',
            name='questions',
            field=models.ManyToManyField(through='signals.CategoryQuestion', to='signals.Question'),
        ),
    ]
