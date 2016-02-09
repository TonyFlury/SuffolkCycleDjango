#!/usr/bin/env python
"""
# SuffolkCycleDjango : Implementation of context_processor.py

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
__created__ = '16 Jan 2016'

from django.conf import settings
from django.http import HttpRequest

def settings_base_url(request):
    return {"BASE_URL": settings.BASE_URL,          # Derived from settings - not ideal
            "HOST": request.get_host(),             # The actually requested URL
            "HOST_URL": 'http://{}/'.format(request.get_host()) }
