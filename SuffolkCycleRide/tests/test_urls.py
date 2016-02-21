#!/usr/bin/env python
"""
# SuffolkCycleDjango : Implementation of test_urls.py

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
__created__ = '19 Feb 2016'


from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse

import views

class C001_TestBasicUrl(TestCase):
    def setUp(self):
        self.client = Client()
        pass

    def tearDown(self):
        pass

    def test_001_010_homepage(self):
        r = self.client.get(reverse('Home'))
        self.assertEqual(r.statuscode, 200)
        self.assertEqual(r.resolver_match.func.__name__, views.home)
        self.assertEqual(r.templates[0], 'SuffolkCycleRide/pages/home.html')