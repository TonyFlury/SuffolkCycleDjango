# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-19 10:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Sponsors', '0009_auto_20160318_1234'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sponsor',
            name='potential',
            field=models.BooleanField(default=True, verbose_name='Potential Sponsor only'),
        ),
    ]
