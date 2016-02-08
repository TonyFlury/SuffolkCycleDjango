# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-29 23:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0006_tag_is_permanent'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='id',
            field=models.AutoField(auto_created=True, default=1, primary_key=True, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='entry',
            name='slug',
            field=models.CharField(db_index=True, default='', editable=False, max_length=60),
        ),
    ]