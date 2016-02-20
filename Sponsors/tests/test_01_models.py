#!/usr/bin/env python
"""
# SuffolkCycleDjango : Implementation of test_01_models

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
__created__ = '20 Feb 2016'


from django.core.exceptions import ValidationError
from django.test import TestCase

import Sponsors.models


class C010_test_Opportunity_Model(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_010_001_Opportunity_creation_one_word_name(self):
        """Test that the slug is created correctly when the name is a single word"""
        opp = Sponsors.models.Opportunity(name='Website')
        opp.save()
        self.assertEqual(opp.slug, 'website')

    def test_010_002_test_Opportunity_creation_two_word_name(self):
        """Test that the slug is created correctly when the name is two words"""
        opp = Sponsors.models.Opportunity(name='Business Cards')
        opp.save()
        self.assertEqual(opp.slug, 'business-cards')

class C020_test_Opportunity_Model(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_020_001_Sponsor_creation_one_word_name(self):
        """Test that the slug is created correctly when the name is a single word"""
        spo = Sponsors.models.Sponsor(name='BT')
        spo.save()
        self.assertEqual(spo.slug, 'bt')

    def test_020_002_test_Sponsor_creation_two_word_name(self):
        """Test that the slug is created correctly when the name is two words"""
        spo = Sponsors.models.Sponsor(name='British Gas')
        spo.save()
        self.assertEqual(spo.slug, 'british-gas')
