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

from SuffolkCycleRide import views
from stats.models import PageVisit

from django.utils.timezone import now
from datetime import timedelta


class C001_TestStaticUrls(TestCase):
    def setUp(self):
        self.client = Client()
        pass

    def tearDown(self):
        pass

    def test_001_010_homepage(self):
        ts = now()
        r = self.client.get(reverse('Home'))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.resolver_match.func.__name__, views.home.__name__)
        self.assertEqual(r.templates[0].name, 'SuffolkCycleRide/pages/home.html')
        self.assertAlmostEqual(PageVisit.most_recent('Home').timestamp, ts, delta=timedelta(milliseconds=100))

    def test_001_011_readmore(self):
        ts = now()
        r = self.client.get(reverse('Readmore'))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.resolver_match.func.__name__, views.readmore.__name__)
        self.assertEqual(r.templates[0].name, 'SuffolkCycleRide/pages/readmore.html')
        self.assertAlmostEqual(PageVisit.most_recent('Readmore').timestamp, ts, delta=timedelta(milliseconds=100))

    def test_001_011_privacy(self):
        ts = now()
        r = self.client.get(reverse('Privacy'))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.resolver_match.func.__name__, views.privacy.__name__)
        self.assertEqual(r.templates[0].name, 'SuffolkCycleRide/pages/privacy.html')
        self.assertAlmostEqual(PageVisit.most_recent('Privacy').timestamp, ts, delta=timedelta(milliseconds=100))


class C002_TestGetInvolved(TestCase):
    def setUp(self):
        self.client = Client()
        pass

    def tearDown(self):
        pass

    def test_001_012_getinvolved(self):
        ts = now()
        r = self.client.get(reverse('GetInvolved'))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.resolver_match.func.__name__, views.GetInvolved.as_view().__name__)
        self.assertEqual(r.templates[0].name, 'base/VerticalForm.html')
        self.assertAlmostEqual(PageVisit.most_recent('GetInvolved').timestamp, ts, delta=timedelta(milliseconds=100))

