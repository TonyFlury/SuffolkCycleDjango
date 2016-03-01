#!/usr/bin/env python
# coding=utf-8
"""
# SuffolkCycleDjango : Implementation of test_00_signals

Summary : 
    <summary of module/class being implemented>
Use Case : 
    As a <actor> I want <outcome> So that <justification>

Testable Statements :
    Can I <Boolean statement>
    ....
"""

from django.test import TestCase
from django.contrib.auth.models import User
from cyclists import models

__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '26 Feb 2016'


class UserCreationSignal(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_010_CreateUser(self):
        """Confirm that a Cyclist instance is created when a User is created"""
        # Confirm these is no Cyclist instance, and then create a new user
        self.assertEqual(len(models.Cyclist.objects.all()),0)
        user = User.objects.create_user( first_name = 'Chester', last_name='Testington',
                                         username='Tester', password='testtest')
        self.assertEqual(len(models.Cyclist.objects.all()),1)

