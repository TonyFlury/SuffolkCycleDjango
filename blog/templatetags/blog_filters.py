#!/usr/bin/env python
"""
# SuffolkCycleDjango : Implementation of blog_filters.py

Summary : 
    <summary of module/class being implemented>
Use Case : 
    As a <actor> I want <outcome> So that <justification>

Testable Statements :
    Can I <Boolean statement>
    ....
"""

from django import template
from django.template.defaultfilters import stringfilter
from blog.models import Tag

from calendar import month_name

__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '06 Feb 2016'

register = template.Library()


@register.filter(name='get_month_name')
def get_month_name(month_number):
    try:
        return month_name[int(month_number)]
    except:
        return ""


@register.filter(name='ellipsis')
@stringfilter
def ellipsis(value, max_length):
    if value < max_length:
        return value
    return value[:max_length - 3] + '...'


@register.filter(name='center_ellipsis')
@stringfilter
def ellipsis(value, max_length):
    if value < max_length:
        return value
    stride = (max_length - 3) / 2
    return value[:stride] + '...' + value[-stride:]

@register.filter(name='get_tag_name')
@stringfilter
def get_tag_name(tag_slug):
    try:
        name =  Tag.objects.get(slug=tag_slug)
    except:
        return ""

    return name