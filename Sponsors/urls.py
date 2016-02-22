#!/usr/bin/env python
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

from django.conf.urls import include, url

from django.contrib import admin

import views

admin.autodiscover()

app_name = "Sponsors"

urlpatterns = [
        url(r'^$', views.main, name='Main'),
        url(r'interest/(?P<opportunity_slug>[\w-]+)$', views.interest.as_view(), name='Interest'),
        ]


