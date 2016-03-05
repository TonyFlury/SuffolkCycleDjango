#!/usr/bin/env python
"""
# SuffolkCycleDjango : Implementation of handlers.py

Summary : 
    <summary of module/class being implemented>
Use Case : 
    As a <actor> I want <outcome> So that <justification>

Testable Statements :
    Can I <Boolean statement>
    ....
"""

__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '24 Jan 2016'

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from cyclists.models import Cyclist

@receiver(post_save, sender=User)
def UserCreate( sender, instance, created, **kwargs):

    if (not created) or instance.is_staff:
        return

    cyc = Cyclist.objects.create( user=instance, currentPledgedAmount=0, targetAmount=0, statement='')
    cyc.save()
