# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-26 23:42
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Sponsors', '0006_auto_20160220_1322'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sponsor',
            name='mobile',
            field=models.CharField(blank=True, help_text='Mobile number - 11 digits only - no spaces or punctuation', max_length=11, validators=[django.core.validators.RegexValidator(message='Mobile number must be entered in digits only - 11 digits only, no spaces.', regex='\\d{11}')]),
        ),
    ]