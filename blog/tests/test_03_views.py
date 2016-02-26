#!/usr/bin/env python
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
from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse

from datetime import datetime
from blog import views
from blog import models

from stats.models import PageVisit

from django.utils.timezone import now
from datetime import timedelta

__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '19 Feb 2016'


class C030_TestViews(TestCase):
    def setUp(self):
        """ Contrived set of entries and tags in order to test most of the list functionality"""
        self.t1 = models.Tag(name='Tag 1', is_permanent=True)
        self.t1.save()
        self.t2 = models.Tag(name='Tag 2', is_permanent=True)
        self.t2.save()
        self.t3 = models.Tag(name='Tag 3', is_permanent=True)
        self.t3.save()
        self.t4 = models.Tag(name='Tag 4', is_permanent=True)
        self.t4.save()

        self.e1 = models.Entry(title="Entry 1")
        self.e1.save()
        self.e2 = models.Entry(title="Entry 2")
        self.e2.save()
        self.e3 = models.Entry(title="Entry 3")
        self.e3.save()
        self.e4 = models.Entry(title="Entry 4")
        self.e4.save()

        self.client = Client()

    def tearDown(self):
        pass

    def test_001_010_no_entries_view_resolver(self):
        """ Test that the /blog/ url resolves to the correct View"""
        p = self.client.get(reverse('blog:Main'))
        self.assertEqual(p.status_code, 200)
        self.assertEqual(p.resolver_match.func.__name__, views.Main.as_view().__name__)

    def test_001_012_PageVisit(self):
        ts = now()
        p = self.client.get(reverse('Blog:Main'))
        self.assertAlmostEqual(PageVisit.most_recent('Blog:Main').timestamp, ts, delta=timedelta(milliseconds=60))

    def test_001_015_no_entries_template(self):
        """ Test that the /blog/ url uses the correct template - don't care about what it extends"""
        p = self.client.get(reverse('Blog:Main'))
        self.assertTemplateUsed(p, 'blog/entry_list.html')

    def test_001_016_no_entries_context(self):
        """Confirm that context is empty when there are no entries"""
        p = self.client.get(reverse('Blog:Main'))
        self.assertEqual(len(p.context[-1]['entries']), 0)
        self.assertEqual(len(p.context[-1]['archive']['list']), 0)
        self.assertEqual(len(p.context[-1]['tags']), 0)

    def test_001_020_single_entry_no_tags(self):
        """Test for a single published entry with no tag confirm that the context is correct"""
        self.e1.content = "This is Entry 1"
        self.e1.pub_date = datetime(2016, 1, 1)
        self.e1.is_published = True
        self.e1.save()
        p = self.client.get(reverse('Blog:Main'))
        self.assertEqual(len(p.context[-1]['entries']), 1)
        self.assertEqual(p.context[-1]['entries'][0], self.e1)
        self.assertEqual(len(p.context[-1]['archive']['list']), 1)
        self.assertEqual(p.context[-1]['archive']['list'][0], self.e1)
        self.assertEqual(len(p.context[-1]['tags']), 0)

    def test_001_021_single_entry_with_tag(self):
        """Test for a single published entry with a tag confirm that the context is correct"""
        self.e1.content = "This is Entry 1"
        self.e1.pub_date = datetime(2016, 1, 1)
        self.e1.is_published = True
        self.e1.save()
        self.e1.tags.add(self.t3)
        self.e1.save()

        p = self.client.get(reverse('Blog:Main'))
        self.assertEqual(len(p.context[-1]['entries']), 1)
        self.assertEqual(p.context[-1]['entries'][0], self.e1)
        self.assertEqual(len(p.context[-1]['archive']['list']), 1)
        self.assertEqual(p.context[-1]['archive']['list'][0], self.e1)
        self.assertEqual(len(p.context[-1]['tags']), 1)
        self.assertEqual(p.context[-1]['tags'][0], self.t3)

    def test_001_030_multiple_entry(self):
        """Test for a multiple published entry with tags"""
        self.e1.content = "This is Entry 1"
        self.e1.pub_date = datetime(2016, 2, 1)
        self.e1.is_published = True
        self.e1.save()

        self.e2.content = "This is Entry 2"
        self.e2.pub_date = datetime(2016, 1, 1)
        self.e2.is_published = True
        self.e2.save()

        self.e3.content = "This is Entry 3"
        self.e3.pub_date = datetime(2015, 12, 1)
        self.e3.is_published = True
        self.e3.save()

        self.e4.content = "This is Entry 4"
        self.e4.pub_date = datetime(2015, 11, 15)
        self.e4.is_published = True
        self.e4.save()

        self.e1.tags.add(self.t1, self.t2, self.t3)
        self.e2.tags.add(self.t1, self.t2)
        self.e3.tags.add(self.t1, self.t3)
        self.e4.tags.add(self.t4)

        p = self.client.get(reverse('Blog:Main'))
        self.assertEqual(len(p.context[-1]['entries']), 4)
        self.assertSequenceEqual(p.context[-1]['entries'], [self.e1, self.e2, self.e3, self.e4])
        self.assertEqual(len(p.context[-1]['archive']['list']), 4)
        self.assertSequenceEqual(p.context[-1]['archive']['list'], [self.e1, self.e2, self.e3, self.e4])
        self.assertEqual(len(p.context[-1]['tags']), 4)
        self.assertSequenceEqual(p.context[-1]['tags'], [self.t1, self.t2, self.t3, self.t4])
        for t in p.context[-1]['tags']:
            if t == self.t1:
                self.assertEqual(t.category, 'upper')
            if t == self.t2 or t == self.t3:
                self.assertEqual(t.category, 'avg')
            if t == self.t4:
                self.assertEqual(t.category, 'lower')

# todo - test cases for unpublished entries - when author is logged in, and when not.
# Todo - Test cases to test searches by tag - and search by Archive (month & year)
# Todo - test cases to test pagination - default is 10 with min 5 orphans
