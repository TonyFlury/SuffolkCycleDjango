#!/usr/bin/env python
"""
# SuffolkCycleDjango : Implementation of test_tags.py

Summary : 
    <summary of module/class being implemented>
Use Case : 
    As a <actor> I want <outcome> So that <justification>

Testable Statements :
    Can I <Boolean statement>
    ....
"""

from django.test import TestCase
from django.template import Template, Context
from django.conf import settings

__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '22 Feb 2016'


class C001_TestTemplateTags(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_001_001AbsoluteStatic(self):
        test_host, test_file = 'test.test', 'a.a'
        TEMPLATE = Template("{% load helper_tags %}{% absolute_static '" + test_file + "' %}")
        rendered = TEMPLATE.render(Context({'HOST':test_host}))
        self.assertEqual(u'http://{}{}{}'.format(test_host,settings.STATIC_URL,test_file), rendered)

