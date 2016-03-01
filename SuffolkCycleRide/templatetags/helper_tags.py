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
from django.forms.boundfield import BoundField

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

@register.simple_tag(name='min', takes_context=False)
def get_min(a,b):
    return min(a,b)

@register.simple_tag(name='max', takes_context=False)
def get_max(a,b):
    return max(a,b)

@register.simple_tag(name='ratio', takes_context=False)
def get_ratio(a,b):
    return 1.0*a / b

@register.simple_tag(name='resize_style', takes_context=False)
def picture_style(picture, max_width=None, max_height=None):
    if isinstance(picture, BoundField):
        print picture
    ratio = min(1.0*int(max_width)/picture.width if max_width else 1.0,
                1.0*int(max_height)/picture.height if max_height else 1.0)
    return format_html('style="width:{};height:{};"'.format(int(picture.width*ratio), int(picture.height*ratio)))

@register.simple_tag(name='limited_width_ratio', takes_context=False)
def limited_width_ratio(value,max_value, max_width ):
    return min( float(max_width), float(max_width)*float(value)/float(max_value))

@register.filter(name='currency')
def currency_filter(value):
    value = str(value)
    if value[-3:] == ".00":
        return value[:-3]
    else:
        return value
