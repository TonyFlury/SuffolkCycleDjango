#!/usr/bin/env python
"""
# SuffolkCycleDjango : Implementation of fields.py

Summary : 
    <summary of module/class being implemented>
Use Case : 
    As a <actor> I want <outcome> So that <justification>

Testable Statements :
    Can I <Boolean statement>
    ....
"""
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from django.db import models
from pickle import loads, dumps

__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '10 Jan 2016'


class DictField( models.Field ):

    description = 'Field to store an arbitary dictionary'

    def __init__(self, *args, **kwargs):
        kwargs['editable'] = False
        super(DictField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(DictField, self).deconstruct()
        return name, path, args, kwargs

    def db_type(self, connection):
        if connection.settings_dict['ENGINE'] == 'django.db.backends.sqlite3':
            return 'TEXT'
        else:
            raise NotImplementedError('Custom DictField not implemented for non sqlite databases')

    @staticmethod
    def parsePickle(value):
        try:
            v = loads(value)
        except (EOFError,KeyError,IndexError):
            raise ValidationError('Database value incorrect for dict instance')

        if not isinstance(v,dict):
            raise ValidationError('Database value incorrect for dict instance')

        return v

    def from_db_value(self, value, expression, connection, context):
        if value is None:
            return value

        return DictField.parsePickle(value)

    def to_python(self, value):
        if isinstance(value, basestring):
            return value

        if value is None:
            return value

        return DictField.parsePickle(value)

    def get_prep_value(self, value):
        if not isinstance(value, dict):
            raise ValidationError("DictField only supports dictionary objects")
        return dumps(value)

    def get_prep_lookup(self, lookup_type, value):
        raise TypeError("Cannot use DictField for lookups or joins")

    def formfield(self, **kwargs):
        # This is a fairly standard way to set up some defaults
        # while letting the caller override them.
        defaults = {'form_class': models.CharField}
        defaults.update(kwargs)
        return super(DictField, self).formfield(**defaults)