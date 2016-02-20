#!/usr/bin/env python
"""
# SuffolkCycleDjango : Implementation of testrunner.py

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


from django.test.runner import DiscoverRunner
from django.test import TestCase
from unittest import TestSuite


class LayeredTestRunner(DiscoverRunner):
    """Specialise Test Runner so that tests per app are run in order - class name.method_name

        Only the class name needs to be ordered.
    """

    def flatten(self, suite):
        a = []

        if issubclass(suite.__class__, TestCase):
           return suite

        for t in suite:
            if isinstance(t, TestSuite):
                a += self.flatten(t)
            else:
                a.append(t)
        return a

    def build_suite(self, test_labels, extra_tests=None, **kwargs):
        suite = super(LayeredTestRunner,self).build_suite(test_labels,extra_tests,**kwargs)
        suite = self.flatten(suite)
        return TestSuite(sorted(suite, key=lambda i:i.id() ))