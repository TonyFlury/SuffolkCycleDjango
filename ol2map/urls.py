#!/usr/bin/env python
# coding=utf-8
"""
# SuffolkCycleDjango : Implementation of urls.py

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
__created__ = '16 Mar 2016'

from django.conf.urls import url

import views

urlpatterns = [
    url(r'^map/(?P<instance>[0-9A-Z]{16})/$', views.json_get, name='ol2Map')
]
