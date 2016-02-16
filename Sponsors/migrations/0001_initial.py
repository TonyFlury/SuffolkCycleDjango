# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-13 00:16
from __future__ import unicode_literals

from django.db import migrations, models
import markitup.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Opportunity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=120)),
                ('slug', models.SlugField(default='')),
                ('description', markitup.fields.MarkupField(no_rendered_field=True)),
                ('max_value', models.DecimalField(blank=True, decimal_places=2, default=None, max_digits=9, null=True)),
                ('value', models.DecimalField(blank=True, decimal_places=2, default=None, max_digits=9, null=True)),
                ('available', models.BooleanField(default=True)),
                ('taken', models.BooleanField(default=False)),
                ('_description_rendered', models.TextField(blank=True, editable=False)),
            ],
        ),
        migrations.CreateModel(
            name='Sponsor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=120)),
                ('slug', models.SlugField(default='')),
                ('website', models.URLField()),
                ('logo_url', models.URLField()),
                ('supports', models.ManyToManyField(related_name='supported_by', to='Sponsors.Opportunity')),
            ],
        ),
    ]