# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-02 11:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0007_auto_20160129_2358'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='id',
            field=models.AutoField(auto_created=True, default=1, primary_key=True, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='tag',
            name='slug',
            field=models.CharField(db_index=True, editable=False, max_length=20),
        ),
    ]