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
from django.template.base import FilterExpression
from django.conf import settings
from django.utils.html import format_html
from django.forms.boundfield import BoundField
from decimal import Decimal

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
    num_types = (Decimal,int,float)

    if not (isinstance(max_value, num_types) and isinstance(value, num_types)) or not (isinstance(max_width, num_types)):
        return 0

    if int(max_value) == 0:
        return 0

    return min( float(max_width), float(max_width)*float(value)/float(max_value))


class varNode(template.Node):
    def __init__(self, parser, value, asvar):

        self.value = FilterExpression(value, parser)
        self.asvar = asvar

    def render(self, context):
        context[self.asvar] = self.value.resolve(context)
        return ''

@register.tag(name='var')
def do_var(parser, token):
    tag = "var"
    try:
        bits = token.split_contents()[1:]
    except ValueError:
        raise template.TemplateSyntaxError(
            "{} tag requires 1 argument and an variable assignment: "
            "<value> as <var>".format(tag) )

    if len(bits) == 3:
            var = bits[0]
            asvar = bits[-1]
    else :
        raise template.TemplateSyntaxError(
            "{} tag requires 1 argument and an variable assignment: "
            "<value> as <var>".format(tag) )

    return varNode( parser, var, asvar )


@register.simple_tag(name='iff', takes_context=False)
def iff(cond, true_value, false_value):
    return true_value if cond else false_value

class iffchangedNode(template.Node):
    def __init__(self, parser, condition, true_value, false_value, asvar=None):
        self.condition = FilterExpression(condition, parser)

        self.true_value = FilterExpression(true_value, parser)
        self.false_value = FilterExpression(false_value, parser)
        self.asvar = asvar

    def render(self, context):
        if self not in context.render_context:
            context.render_context[self] = {'condition': self.condition.resolve(context)}
            if self.asvar:
                context[self.asvar] = self.true_value.resolve(context)
            return self.true_value.resolve(context)
        else:
            if context.render_context[self]['condition'] == self.condition.resolve(context):
                if self.asvar:
                    context[self.asvar] = self.false_value.resolve(context)
                else:
                    return self.false_value.resolve(context)
            else:
                context.render_context[self]['condition'] = self.condition.resolve(context)
                if self.asvar:
                    context[self.asvar] = self.true_value.resolve(context)
                else:
                    return self.true_value.resolve(context)

        return ''

@register.tag(name='iffchanged')
def do_iffchanged(parser, token):
    tag = "iffchanged"
    try:
        bits = token.split_contents()[1:]
    except ValueError:
        raise template.TemplateSyntaxError(
            "{} tag requires  3 arguments (with an optional variable assignment): "
            "<condition> <true_value> <false_value> [as <var>]".format(tag) )

    asvar = None
    if (len(bits) == 5) and (bits[-2].lower() == 'as'):
            bits = bits[:-2]
            asvar = bits[-1]
    elif len(bits) != 3:
        raise template.TemplateSyntaxError(
                "{} tag requires  3 arguments (with an optional variable assignment): <condition> <true_value> <false_value> [as <var>]".format(tag) )
    return iffchangedNode(parser, *[bit for bit in bits], asvar=asvar)


@register.filter(name='currency')
def currency_filter(value):
    value = str(value)
    if value[-3:] == ".00":
        return value[:-3]
    else:
        return value

@register.filter(name='kmToMiles')
def kmToMiles(value):
    return "{:.1f}".format(float(value)*0.6224)
