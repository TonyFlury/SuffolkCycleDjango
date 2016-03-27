#!/usr/bin/env python
# coding=utf-8
"""
# SuffolkCycleDjango : Implementation of ExtTestCase.TestCase

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
__created__ = '11 Mar 2016'

import django.test
from bs4 import BeautifulSoup
from collections import Iterable

class NameNotFound(BaseException):
    pass

class TestCase( django.test.TestCase):
    """Extend Test case to add some nice/nicer assertions - remove some clutter from test cases"""

    def _traverseContext(self, context, attr_name):
        """ Internal method to traverse a context with a dotted attribute name - and return the accessed value
        :param context: The context dictionary mapping object
        :param attr_name: The dotted attribute name to be found
        :return: the context as access from the dotted attribute name or returns None
        """
        keys = attr_name.split('.')
        val = context
        for ind, key in enumerate(keys):
            if key not in val:
                   raise NameNotFound
            val = val[key]
        else:
            return val

    def assertInContext(self, response, attr_name, expected=None, **kwargs):
        """Check that keyword exists in top most context, and the value equals the optional value"""

        try:
            val = self._traverseContext(response.context[-1], attr_name)
        except NameNotFound:
            self.fail(kwargs.get('msg',
                        "Attr '{}' does not exist in response context".format( attr_name ) ))

        if expected is not None:
            if isinstance(expected,Iterable) and isinstance(val,Iterable):
                self.assertSequenceEqual(
                        expected, val,
                        msg=kwargs.get('msg',"context variable '{}': expected '{}', actual '{}'".format(attr_name, expected, val)),
                        seq_type=kwargs.get('seq_type',None))
            else:
                if expected != val:
                    self.fail(kwargs.get('msg',"context variable '{}': expected '{}'', actual'{}'".format(attr_name, expected, val)))

    def assertNotInContext(self, response, attr_name, **kwargs):
        """Check that a dotted attribute name does not exist in the response context"""
        try:
            self._traverseContext(response.context[-1], attr_name)
        except NameNotFound:
            return

        self.fail(kwargs.get('msg',
                    "Attr '{}' exists in response context".format( attr_name ) ))

    def assertSelectedHTMLContains(self, content, selector, text, **kwargs):
        """Check that the content when matched against a selector contains the expected text"""
        st = BeautifulSoup(content, 'html5lib')
        selected_tags = st.select(selector)
        if not selected_tags:
            self.fail(kwargs.get('msg',
                         "Nothing matching '{}' selector exists in response context".format(selector) ))

        if not any(text in tag for tag in selected_tags):
            self.fail(kwargs.get('msg',
                        "No text matching '{}' in any tag matching selector '{}'".format(text, selector) ))

    def assertHTMLNotMatchSelector(self, content, selector, **kwargs):
        st = BeautifulSoup(content, 'html5lib')
        selected_tags = st.select(selector)

        if selected_tags:
            self.fail(kwargs.get('msg',
                         "'{}' selector exists in response context".format(selector) ))

    def assertHTMLMatchSelector(self, content, selector, **kwargs):
        st = BeautifulSoup(content, 'html5lib')
        selected_tags = st.select(selector)

        if not selected_tags:
            self.fail(kwargs.get('msg',
                         "'{}' selector does not exists in response context".format(selector) ))
