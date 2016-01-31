#!/usr/bin/env python
"""
# SuffolkCycleRide : Implementation of dashboard_url

Summary :
    Implementation of dashboard URLs - separated from the other url file to compartmentalise the dashboard.

Use Case :
    As a <actor> I want <outcome> So that <justification>

Testable Statements :
    Can I <Boolean statement>
    ....
"""

__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '23 Jan 2016'

from django.conf.urls import url

import views

app_name = "dashboard"

urlpatterns = [
    url(r'^$', views.UserDashboard.as_view(), name='Home'),
    url(r'^MyDetails$', views.MyDetails.as_view(), name='MyDetails'),
    url(r'PasswordReset$', views.PasswordReset.as_view(), name="PasswordReset"),
    url(r'^CycleRoutes$', views.CycleRoutes.as_view(), name='CycleRoutes'),
    url(r'^Volunteering$', views.OtherVolunteering.as_view(), name='OtherVolunteering'),
    url(r'^Fundraising$', views.Fundraising.as_view(), name='FundRaising'),
]

