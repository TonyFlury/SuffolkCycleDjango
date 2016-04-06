#!/usr/bin/env python
# coding=utf-8
"""
# SuffolkCycleDjango : Implementation of map_tags.py

Summary : 
    <summary of module/class being implemented>
Use Case : 
    As a <actor> I want <outcome> So that <justification>

Testable Statements :
    Can I <Boolean statement>
    ....
"""
import os.path
import ol2map.models
import cyclists.models
from django import template
from django.utils.html import mark_safe

__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '04 Apr 2016'


register = template.Library()


@register.simple_tag(name='MapForLeg', takes_context=True)
def MapForLeg(context, leg):
    assert isinstance(leg, cyclists.models.Leg)
    context_name = 'ol2map_{}'.format(leg.name)
    themap = ol2map.models.ol2Map(domElement=context_name,
                                  classes = ['smallmap'],
                                  restrictedExtent = ((0.2, 52.6), (1.95, 51.5)),
                                  center = (1.245, 52.254),
                                  zoom = 0,
                                  zoomExtent = (8,16),
                                  numZoomLevel = 9,
                                  kmlLayers=[(leg.name,os.path.join('/media', leg.map.name), True, False)],
                                  switcher = True )
    return themap()