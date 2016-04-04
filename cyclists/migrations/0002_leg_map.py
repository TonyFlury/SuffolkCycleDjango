# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-04-04 09:32
from __future__ import unicode_literals

import cyclists.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cyclists', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='leg',
            name='map',
            field=models.FileField(blank=True, upload_to=cyclists.models.get_map_path),
        ),
    ]
