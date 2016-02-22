#!/usr/bin/env python
"""
# SuffolkCycleDjango : Implementation of blog_tags.py

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
__created__ = '07 Feb 2016'

from django import template
from django.core.urlresolvers import reverse
from django.utils.html import format_html, mark_safe

register = template.Library()


@register.simple_tag(name='ellipsis')
def add_ellipsis(string, length=30, center=False):
    if not isinstance(string, basestring):
        return ""

    if len(string) <= length:
        return string

    if center:
        stride = min((len(string) - 3) / 2, (length - 3) / 2)
        print "{} : stride {}".format(string, stride)
        return string[:stride] + '...' + string[-stride:]
    else:
        return string[:length - 3] + '...'


@register.simple_tag(name='year_visible', takes_context=True)
def year_visible(context):
    if int(context['archive']['display_year']) == int(context['year']['grouper']):
        return mark_safe("archive-visible")


@register.simple_tag(name='month_visible', takes_context=True)
def month_visible(context):
    if (int(context['archive']['display_year']) == int(context['year']['grouper'])) and (
                int(context['archive']['display_month']) == int(context['month']['grouper'])):
        return mark_safe("archive-visible")


@register.simple_tag(name='year_url', takes_context=True)
def year_url(context):
    year = "{:4d}".format(int(context['year']['grouper']))
    return reverse('blog:Archive', kwargs={'year': year})


@register.simple_tag(name='month_url', takes_context=True)
def year_url(context):
    year = "{:4d}".format(int(context['year']['grouper']))
    month = "{:02d}".format(int(context['month']['grouper']))
    return reverse('blog:Archive', kwargs={'year': year, 'month': month})


def build_url(text, page, context):

    tag = context['args'].get('tag_slug', None)
    year = context['args'].get('year', None)
    month = context['args'].get('month', None)

    if not tag and not year and not month:
        return format_html('<a href="{url}">{text}</a>',
                            url = reverse('blog:Main', kwargs={'page':page} ),
                            text = text)

    if tag:
        return format_html('<a href="{url}">{text}</a>',
                            url = reverse('blog:Search', kwargs={'tag_slug':tag, 'page':page} ),
                            text = text)

    if year and not month:
        return format_html('<a href="{url}">{text}</a>',
                            url = reverse('blog:Archive', kwargs={'year':year, 'page':page} ),
                            text = text)

    if year and month:
                return format_html('<a href="{url}">{text}</a>',
                            url = reverse('blog:Archive', kwargs={'year':year, 'month':month, 'page':page} ),
                            text = text)


@register.simple_tag(name='prev_page_url', takes_context=True)
def prev_page_url(context):

    prev_page = context['args'].get('prev_page', None)
    if not prev_page : # Page count starts from one
        return ""

    return build_url('Previous', prev_page, context)


@register.simple_tag(name='next_page_url', takes_context=True)
def next_page_url(context):

    next_page = context['args'].get('next_page', None)
    if not next_page:
        return ""

    return build_url('Next', next_page, context)

