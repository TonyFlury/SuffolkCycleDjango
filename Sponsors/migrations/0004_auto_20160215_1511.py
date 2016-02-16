# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-15 15:11
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Sponsors', '0003_auto_20160214_1206'),
    ]

    operations = [
        migrations.AddField(
            model_name='sponsor',
            name='potentials',
            field=models.ManyToManyField(related_name='potentially_supported_by', to='Sponsors.Opportunity'),
        ),
        migrations.AlterField(
            model_name='sponsor',
            name='communication_preference',
            field=models.CharField(choices=[('email', 'email'), ('telephone', 'telephone'), ('mobile', 'mobile')], default='email', max_length=10),
        ),
        migrations.AlterField(
            model_name='sponsor',
            name='mobile',
            field=models.CharField(blank=True, help_text='Mobile number - 11 digits only - no spaces or punctuation', max_length=11, validators=[django.core.validators.RegexValidator(message='Phone number must be entered in digits only - 11 digits only, no spaces.', regex='\\d{11}')]),
        ),
        migrations.AlterField(
            model_name='sponsor',
            name='telephone',
            field=models.CharField(blank=True, help_text='Telephone number - 11 digits only - no spaces or punctuation', max_length=11, validators=[django.core.validators.RegexValidator(message='Full phone number must be entered - 11 digits only, no spaces or punctuation.', regex='\\d{11}')]),
        ),
        migrations.AlterField(
            model_name='sponsor',
            name='website',
            field=models.URLField(blank=True),
        ),
    ]