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
from Sponsors import views
from Sponsors import models
from Sponsors import forms

from stats.models import PageVisit

from django.utils.timezone import now
from datetime import timedelta

class OpportunityPage(TestCase):

    def setUp(self):
        self.opp1 = models.Opportunity(name='opp1', value=1)
        self.opp1.save()
        self.opp2 = models.Opportunity(name='opp2', value=2)
        self.opp2.save()
        self.opp3 = models.Opportunity(name='opp3', max_value=3)
        self.opp3.save()
        self.opp4 = models.Opportunity(name='opp4', value=4)
        self.opp4.save()
        self.client = Client()

    def test_001_basic_get(self):
        """Check that Main page is fetchable"""
        p = self.client.get(reverse('Sponsorship:Main'))
        self.assertEqual(p.status_code,200)
        self.assertEqual(p.resolver_match.func.__name__, views.main.__name__)

    def test_002_basic_get_template_check(self):
        """Check main page is served by correct template"""
        p = self.client.get(reverse('Sponsorship:Main'))
        self.assertTemplateUsed(p, 'Sponsors/main.html')

    def test_003_basic_get_context_check(self):
        """Check that context is correct - in the correct order"""
        p = self.client.get(reverse('Sponsorship:Main'))
        self.assertEqual(len(p.context[-1]['available']), 4)
        self.assertSequenceEqual(p.context[-1]['available'], [self.opp1, self.opp2, self.opp3, self.opp4])

    def test_004_basic_get_PageVisitStats(self):
        """Check that the Sponsorship Main page fetch is correctly record as a Visit"""
        ts = now()
        p = self.client.get(reverse('Sponsorship:Main'))
        self.assertAlmostEqual(
                    PageVisit.most_recent('Sponsorship:Main').timestamp, ts, delta=timedelta(milliseconds=50))

    def test_010_test_unavailable(self):
        """Test that an opportunity marked as unavailable is not listed"""
        self.opp2.available = False
        self.opp2.save()
        p = self.client.get(reverse('Sponsorship:Main'))
        self.assertEqual(len(p.context[-1]['available']), 3)
        self.assertSequenceEqual(p.context[-1]['available'], [self.opp1, self.opp3, self.opp4])

    def test_020_test_taken(self):
        """Test that an opportunity marked as taken is not listed"""
        self.opp3.taken = True
        self.opp3.save()
        p = self.client.get(reverse('Sponsorship:Main'))
        self.assertEqual(len(p.context[-1]['available']), 3)
        self.assertSequenceEqual(p.context[-1]['available'], [self.opp1, self.opp2, self.opp4])

    def test_030_test_value_changed(self):
        """Opportunities are listed in value order - not creation time - which might be implied by earlier tests"""
        self.opp2.value=10
        self.opp2.save()
        p = self.client.get(reverse('Sponsorship:Main'))
        self.assertEqual(len(p.context[-1]['available']), 4)
        self.assertSequenceEqual(p.context[-1]['available'], [self.opp1, self.opp3, self.opp4, self.opp2])

    def test_035_test_max_value_changed(self):
        """Opportunities are listed in max_value order - not creation time - which might be implied by earlier tests"""
        self.opp3.max_value=10
        self.opp3.save()
        p = self.client.get(reverse('Sponsorship:Main'))
        self.assertEqual(len(p.context[-1]['available']), 4)
        self.assertSequenceEqual(p.context[-1]['available'], [self.opp1, self.opp2, self.opp4, self.opp3])

class InterestPage(TestCase):
    def setUp(self):
        self.opp1 = models.Opportunity(name='opp1', value=1)
        self.opp1.save()
        self.client = Client()

    def tearDown(self):
        pass

    def test_001_InterestPageGet(self):
        p = self.client.get(reverse('Sponsorship:Interest', kwargs={'opportunity_slug':self.opp1.slug}))
        self.assertEqual(p.status_code,200)
        self.assertEqual(p.resolver_match.func.__name__, views.interest.as_view().__name__)

    def test_002_InterestPageGet_template(self):
        ts = now()
        p = self.client.get(reverse('Sponsorship:Interest', kwargs={'opportunity_slug':self.opp1.slug}))
        self.assertTemplateUsed(p, 'Sponsors/communicate.html')
        self.assertAlmostEqual( PageVisit.most_recent('Sponsorship:Interest').timestamp, ts, delta=timedelta(milliseconds=100) )

    def test_003_InterestPageGet_context(self):
        p = self.client.get(reverse('Sponsorship:Interest', kwargs={'opportunity_slug':self.opp1.slug}))
        self.assertIsInstance(p.context[-1]['form'], forms.Communications )
        self.assertEqual(p.context[-1]['form']['opportunity'].value(), self.opp1.id)
        self.assertEqual(p.context[-1]['description'],
                         'Thank you for your interest in sponsoring our {}.\n'
                         'Please complete the form, and we will contact you shortly.'.format(self.opp1.name) )

    def test_010_InterestPagePost(self):
        p = self.client.post(reverse('Sponsorship:Interest', kwargs={'opportunity_slug':self.opp1.slug}),
                             data={'opportunity':self.opp1.id,
                              'name':'test Sponsor',
                              'communication_preference':'telephone',
                              'telephone':'11111111111'})
        self.assertEqual(p.templates[0].name, 'Sponsors/communicate.html')
        self.assertEqual(p.context[-1]['confirmation'],True)
        sp = models.Sponsor.objects.all()
        self.assertEqual(len(sp),1)
        self.assertEqual(sp[0].name, 'test Sponsor')
        self.assertEqual(sp[0].potential, True)
        self.assertTrue(self.opp1 in sp[0].potentials.all())