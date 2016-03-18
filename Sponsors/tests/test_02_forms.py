#!/usr/bin/env python
"""
# SuffolkCycleDjango : Implementation of test_02_forms.py

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

from django.test import TestCase
from Sponsors import models
from Sponsors import forms


class C010_test_CommunicationForm(TestCase):
    def setUp(self):
        self.opp1 = models.Opportunity(name='opp1', value=1)
        self.opp1.save()

    def test_010_010_test_FormNameMandatory(self):
        f = forms.Communications(data={'opportunity': self.opp1.id})
        self.assertEqual(f.is_valid(), False)
        self.assertEqual(f.errors['company_name'], [u"You must provide either a 'Company Name' or 'Contact Name'"])

    def test_010_020_test_Form_No_Pref(self):
        f = forms.Communications(data={'opportunity': self.opp1.id,
                                       'contact_name': 'Me',
                                       'communication_preference': ''})
        self.assertEqual(f.is_valid(), False)
        self.assertEqual(f.errors['communication_preference'],
                         [u'You must select your preferred communication method'])

    def test_010_025_test_Form_Invalid_Pref(self):
        f = forms.Communications(data={'opportunity': self.opp1.id,
                                       'contact_name': 'Me',
                                       'communication_preference': 'xxx'})
        self.assertEqual(f.is_valid(), False)
        self.assertEqual(f.errors['communication_preference'],
                         [u'Select a valid choice. xxx is not one of the available choices.'])

    def test_010_028_test_Form_Pref_No_Data(self):
        f = forms.Communications(data={'opportunity': self.opp1.id,
                                       'contact_name': 'Me',
                                       'communication_preference': 'telephone'})
        self.assertEqual(f.is_valid(), False)
        self.assertEqual(f.errors['__all__'],
                         [u'You must provide at least an email address, telephone number or mobile phone number'])

    def test_010_031_test_Form_No_Mobile(self):
        f = forms.Communications(data={'opportunity': self.opp1.id,
                                       'contact_name': 'Me',
                                       'communication_preference': 'mobile',
                                       'telephone':'11111111111'})
        self.assertEqual(f.is_valid(), False)
        self.assertEqual(f.errors['__all__'],
                         [u"'mobile' selected as your preferred contact method, but mobile number not provided"])

    def test_010_032_test_Form_No_Telephone(self):
        f = forms.Communications(data={'opportunity': self.opp1.id,
                                       'contact_name': 'Me',
                                       'communication_preference': 'telephone',
                                       'mobile':'11111111111'})
        self.assertEqual(f.is_valid(), False)
        self.assertEqual(f.errors['__all__'],
                         [u"'telephone' selected as your preferred contact method, but telephone number not provided"])


    def test_010_033_test_Form_No_Email(self):
        f = forms.Communications(data={'opportunity': self.opp1.id,
                                       'contact_name': 'Me',
                                       'communication_preference': 'email',
                                       'mobile':'11111111111'})
        self.assertEqual(f.is_valid(), False)
        self.assertEqual(f.errors['__all__'],
                         [u"'email' selected as your preferred contact method, but email address not provided"])

    def test_010_040_test_Form_Invalid_Email(self):
        f = forms.Communications(data={'opportunity': self.opp1.id,
                                       'contact_name': 'Me',
                                       'communication_preference': 'email',
                                       'email':'a.b.com'})
        self.assertEqual(f.is_valid(), False)
        self.assertEqual(f.errors['email'], [u'Enter a valid email address.'])

    def test_010_041_test_Form_Invalid_Mobile(self):
        f = forms.Communications(data={'opportunity': self.opp1.id,
                                       'contact_name': 'Me',
                                       'communication_preference': 'mobile',
                                       'mobile':'999999'})
        self.assertEqual(f.is_valid(), False)
        self.assertEqual(f.errors['mobile'],
                         [u'Mobile number must be entered in digits only - 11 digits only, no spaces.'])

    def test_010_041_test_Form_Invalid_Phone(self):
        f = forms.Communications(data={'opportunity': self.opp1.id,
                                       'contact_name': 'Me',
                                       'communication_preference': 'telephone',
                                       'telephone':'999999'})
        self.assertEqual(f.is_valid(), False)
        self.assertEqual(f.errors['telephone'],
                         [u'Full phone number must be entered - 11 digits only, no spaces or punctuation.'])