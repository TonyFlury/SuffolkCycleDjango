#!/usr/bin/env python
# coding=utf-8
"""
# SuffolkCycleDjango : Implementation of test_03_views.py

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
__created__ = '08 Mar 2016'

from django.test import TestCase, Client

class Home(TestCase):
    def setup(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_011_PageAccess(self):
        ts = now()
        r = self.client.get(reverse('Readmore'))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.resolver_match.func.__name__, views.readmore.__name__)
        self.assertEqual(r.templates[0].name, 'SuffolkCycleRide/pages/newsletter.html')
        self.assertAlmostEqual(PageVisit.most_recent('Readmore').timestamp, ts, delta=timedelta(milliseconds=100))
