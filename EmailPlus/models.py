#!/usr/bin/env python
"""
# SuffolkCycle : Implementation of models.py

Summary :
    <summary of module/class being implemented>
Use Case :
    As a <actor> I want <outcome> So that <justification>

Testable Statements :
    Can I <Boolean statement>
    ....
"""

from __future__ import unicode_literals

from django.contrib import admin
from django.db import models
from django.utils.timezone import now


class EmailQueue(models.Model):
    queue_time = models.DateTimeField( default=now, db_index=True)
    body_text = models.TextField( db_index=True, null=True)
    subject = models.CharField( max_length=160, default="" )
    sent = models.BooleanField(default=False)
    sent_time = models.DateTimeField(default=now, db_index=True)
    destination = models.EmailField(default="")


# noinspection PyProtectedMember
class EmailQueueAdmin(admin.ModelAdmin):
    list_display = [field.name for field in EmailQueue._meta.fields if field.name != "id"]
