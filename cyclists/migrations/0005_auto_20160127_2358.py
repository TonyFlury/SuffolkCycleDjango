# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-27 23:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cyclists', '0004_auto_20160125_1450'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cyclist',
            name='expectedAmount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=7),
        ),
    ]
