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

    Relevant Documentation :
        Django custom Aggregation Functions :
            https://docs.djangoproject.com/en/1.9/ref/models/expressions/#creating-your-own-aggregate-functions

        sqlite custom aggregators : connection.create_aggregate
            https://docs.python.org/2.7/library/sqlite3.html?highlight=sqlite#connection-objects

"""

__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '06 Feb 2016'

from django.db.backends.signals import connection_created
from django.dispatch import receiver
from django.db.models import Aggregate, FloatField, IntegerField

from math import sqrt

from collections import Counter


class StatsAggregate(Aggregate):
    """ Base Django Aggregation class for Project custom Stats Aggregate implementations """
    def __ror__(self, other):
        raise NotImplemented('Logical OR not implemented')

    def __or__(self, other):
        raise NotImplemented('Logical OR not implemented')

    def __rand__(self, other):
        raise NotImplemented('Logical AND not implemented')

    def __and__(self, other):
        raise NotImplemented('Logical AND not implemented')


class Variance(StatsAggregate):
    """ Defines a Variance( expression ) aggregator - which can be used from a django queryset"""
    function = 'Variance'                           # The name of the function in the queryset
    template = '%(function)s( %(expressions)s )'    # The template used in the SQL query
    name = 'Variance'                               # ToDo - Identify why the name attribute is required

    def __init__(self, expression, **extra):
        super(Variance, self).__init__(
            expression,
            output_field=FloatField(),
            **extra)


class VarianceImp(object):
    """ Class to implement the Variance Aggregator, As per the SQLite custom function protocol"""
    def __init__(self):
        """Called at the start of the Query"""
        self.items = []

    # noinspection PyIncorrectDocstring
    def step(self, value):
        """Called once for each row"""
        self.items.append(value)

    def finalize(self):
        """Called at the end of the query"""
        mean = 1.0 * sum(self.items)/len(self.items)
        return 1.0 * sum(((1.0 * i)-mean)**2 for i in self.items)/len(self.items)


class Mode(StatsAggregate):
    """ Defines a Mode( expression ) aggregator - which can be used from a django queryset"""
    function = 'Mode'
    template = '%(function)s( %(expressions)s )'
    name = 'Mode'

    def __init__(self, expression, **extra):
        super(Mode, self).__init__(
            expression,
            output_field=IntegerField(),
            **extra)


class ModeImp(object):
    def __init__(self):
        self.items = []

    def step(self, value):
        if not isinstance(value, int):
            raise TypeError('Can only use Mode when all data are Integers')
        self.items.append(value)

    def finalize(self):
        return Counter(self.items).most_common(1)[0][0]


class StdDev(StatsAggregate):
    """ Defines a StdDev( expression ) aggregator - which can be used from a django queryset"""
    function = 'StdDev'
    template = '%(function)s( %(expressions)s )'
    name = 'StdDev'

    def __init__(self, expression, **extra):
        super(StdDev, self).__init__(
            expression,
            output_field=FloatField(),
            **extra)


class StdDevImp(object):
    def __init__(self):
        self.items = []

    def step(self, value):
        self.items.append(value)

    def finalize(self):
        mean = 1.0 * sum(self.items)/len(self.items)
        return sqrt(1.0 * sum(((1.0 * i)-mean)**2 for i in self.items)/len(self.items))


# noinspection PyIncorrectDocstring
@receiver(connection_created)
def extend_sqlite(connection=None, **kwargs):
    """Detect any and all new connections and add aggregate functions"""
    if connection.vendor == 'sqlite':
        connection.connection.create_aggregate("StdDev", 1, StdDevImp)
        connection.connection.create_aggregate("Mode", 1, ModeImp)
        connection.connection.create_aggregate("Variance", 1, VarianceImp)




