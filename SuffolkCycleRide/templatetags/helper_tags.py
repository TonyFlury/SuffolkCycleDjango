#!/usr/bin/env python
"""
# SuffolkCycleDjango : Implementation of helper_tags.py

Summary : 
    <summary of module/class being implemented>
Use Case : 
    As a <actor> I want <outcome> So that <justification>

Testable Statements :
    Can I <Boolean statement>
    ....


See : https://docs.djangoproject.com/en/1.9/howto/custom-template-tags/
"""
from django import template
from django.conf import settings
from django.utils.html import format_html

__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '09 Feb 2016'


register = template.Library()


# noinspection PyIncorrectDocstring
@register.simple_tag(name='absolute_static', takes_context=True)
def absolute_static(context, local_path):
    """Missing counterpart to the default static tag - returns the absolute URL for the any local static file"""
    if not local_path:
        return ""
    if not settings.STATIC_URL.startswith('/'):                 #TODO - this path not tested as yet
        return format_html('{static}{path}'.format(
                            static = settings.STATIC_URL,
                            path = local_path))
    else:
        return format_html( "http://{host}{static}{path}".format(
                            host = context['HOST'],
                            static = settings.STATIC_URL,
                            path = local_path))