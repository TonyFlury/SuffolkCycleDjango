#!/usr/bin/env python
"""
# SuffolkCycleDjango : Implementation of aggregates.py

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
__created__ = '06 Feb 2016'

from django.db.backends.signals import connection_created
from django.dispatch import receiver
from django.db.models import Aggregate, FloatField, IntegerField

from math import sqrt

from collections import Counter

class Variance(Aggregate):
    # supports MySum(distinct field)
    function = 'Variance'
    template = '%(function)s( %(expressions)s )'
    name = 'Variance'

    def __init__(self, expression, **extra):
        super(Variance, self).__init__(
            expression,
            output_field=FloatField(),
            **extra)

class VarianceImp:
    def __init__(self):
        self.items = []

    def step(self, value):
        self.items.append(value)

    def finalize(self):
        mean = 1.0 * sum(self.items)/len(self.items)
        return 1.0 * sum(((1.0 * i)-mean)**2 for i in self.items)/len(self.items)

class Mode(Aggregate):
    # supports MySum(distinct field)
    function = 'Mode'
    template = '%(function)s( %(expressions)s )'
    name = 'Mode'

    def __init__(self, expression, **extra):
        super(Mode, self).__init__(
            expression,
            output_field=IntegerField(),
            **extra)

class ModeImp:
    def __init__(self):
        self.items = []

    def step(self, value):
        if not isinstance(value, int):
            raise TypeError('Can only use Mode when all data are Integers')
        self.items.append(value)

    def finalize(self):
        return Counter(self.items).most_common(1)[0][0]

class StdDev(Aggregate):
    # supports MySum(distinct field)
    function = 'StdDev'
    template = '%(function)s( %(expressions)s )'
    name = 'StdDev'

    def __init__(self, expression, **extra):
        super(StdDev, self).__init__(
            expression,
            output_field=FloatField(),
            **extra)

class StdDevImp:
    def __init__(self):
        self.items = []

    def step(self, value):
        self.items.append(value)

    def finalize(self):
        mean = 1.0 * sum(self.items)/len(self.items)
        return sqrt(1.0 * sum(((1.0 * i)-mean)**2 for i in self.items)/len(self.items))

@receiver(connection_created)
def extend_sqlite(connection=None, **kwargs):
    if connection.vendor == 'sqlite':
        connection.connection.create_aggregate("StdDev", 1, StdDevImp)
        connection.connection.create_aggregate("Mode", 1, ModeImp)
        connection.connection.create_aggregate("Variance", 1, VarianceImp)




