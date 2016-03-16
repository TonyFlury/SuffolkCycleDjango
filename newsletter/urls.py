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

__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '12 Jan 2016'


from django.conf.urls import include, url

import views

app_name = 'Newsletter'

urlpatterns = [
    url(r'^$', views.main, name='Home'),
    url(r'^unsubscribe/(?P<email>.*?)$', views.Unsubscribe.as_view(), name='Unsubscribe'),
    url(r'^unsubscribe/$', views.Unsubscribe.as_view(), name='Unsubscribe'),
    url(r'^upload$', views.Upload.as_view(), name='Upload'),
    url(r'^download/(?P<id>[0-9]*?)$', views.Download, name='Download'),
#    url(r'^list$', List, name="List"),
]
