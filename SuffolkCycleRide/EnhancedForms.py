#!/usr/bin/env python
"""
# SuffolkCycleDjango : Implementation of MultipleFormMixin

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
__created__ = '21 Jan 2016'

from django import forms


# Experimental mixin to provide the ability to combile multiple ModelForms into a single form.
# Depends on a template being available to loop and render forms.
# Makes very few assumptions about the content of the template
class CombinedFormBase(forms.Form):
    form_classes = []

    def __init__(self, *args, **kwargs):
        pkwargs = kwargs.copy()
        if 'instance' in pkwargs:
            del pkwargs['instance']

        super(CombinedFormBase, self).__init__(*args, **pkwargs)
        for f in self.form_classes:
            pkwargs = kwargs.copy()
            if 'instance' in kwargs and isinstance(kwargs['instance'],list):
                instance = [i for i in kwargs['instance'] if isinstance(i, f.Meta.model)]
                instance = instance[0] if instance else None
                del pkwargs['instance']
                if instance:
                    pkwargs['instance'] = instance

            name = f.__name__.lower()
            setattr(self, name, f(*args, **pkwargs))
            form = getattr(self, name)
            self.fields.update(form.fields)
            self.initial.update(form.initial)

    def is_valid(self):
        isValid = True
        for f in self.form_classes:
            name = f.__name__.lower()
            form = getattr(self, name)
            if not form.is_valid():
                isValid = False
        # is_valid will trigger clean method
        # so it should be called after all other forms is_valid are called
        # otherwise clean_data will be empty
        if not super(CombinedFormBase, self).is_valid() :
            isValid = False
        for f in self.form_classes:
            name = f.__name__.lower()
            form = getattr(self, name)
            self.errors.update(form.errors)
        return isValid

    def clean(self):
        cleaned_data = super(CombinedFormBase, self).clean()
        for f in self.form_classes:
            name = f.__name__.lower()
            form = getattr(self, name)
            cleaned_data.update(form.cleaned_data)
        return cleaned_data


class MultipleFormMixin(object):
    """ Multiple Form Mixin
        Looks for an Attribute named 'context_template' which is expected to be a dictionary.
        This dictionary is processed recursively (including any lists within the dictionary)
        If the value is a basic Form class, the value is replaced with a instantiated object of this class.
            If a key named 'prefix' exists within the same dictionary as a Form class, then the value is used as the prefix
            attribute into the class instantiation - it is also retained as a tag

        Sets the following attributes :
            'self.context' = a fully interpreted set of values from 'context_template'
             'self.this_form' = the actual form which have been submitted based on the value of the submit
        """
    context_template = {}

    def _context_list(self, original_list, request_data):
        result_list = []
        for item in original_list:
            if isinstance(item, dict):
                result_list.append(self._context_dict(item, request_data))
                continue

            if isinstance(item, list):
                result_list.append(self._context_list(item, request_data))
                continue

            # Highly unlikely we will get here
            if isinstance(item, type) and issubclass(item, django.forms.forms.BaseForm):
                # in this case no chance of identifying which form to pass the request_data to
                result_list.append( item() )
                continue

            result_list.append(item)

        return result_list

    def _context_dict(self, original_dict, request_data):
        result_dict = dict()

        form_class, form_tag, prefix = None, None, None

        for k,v in original_dict.iteritems():

            if isinstance(v, list):
                result_dict[k] = self._context_list(v, request_data)
                continue

            if isinstance(v, dict):
                result_dict[k] = self._context_dict(v, request_data)
                continue

            if isinstance(v, type) and issubclass(v, forms.forms.BaseForm):
                form_tag, form_class = k, v
                continue

            if k == 'prefix':
                prefix = v

            result_dict[k] = v

        # Did we find a form : if so does this form need the request data ?
        if form_class and form_tag:

            if request_data and 'submit' in request_data and (result_dict['submit'] == request_data['submit']):
                result_dict[form_tag] = form_class(data=request_data, prefix = prefix or '')
                self.this_form = result_dict[form_tag]
            else:
                result_dict[form_tag] = form_class(prefix = prefix or '' )

        return result_dict

    def __init__(self, *args, **kwargs):

        if not hasattr(self, 'context_template'):
            raise AttributeError("'context_template' attribute must be defined")

        if not isinstance(self.context_template, dict):
            raise AttributeError("'context' attribute must be a dictionary")

        self.context, self.this_form = None, None

        # noinspection PyArgumentList
        super(MultipleFormMixin,self).__init__(*args,**kwargs)

    # noinspection PyIncorrectDocstring
    def get(self, request, *args, **kwargs):
        """ Set the self.forms and the self.this_form attributes based on the self._forms Meta data"""
        request_data = request.GET if request.GET else None
        self.context = self._context_dict(self.context_template, request_data)

    # noinspection PyIncorrectDocstring
    def post(self, request, *args, **kwargs):
        """ Set the self.forms and the self.this_form attributes based on the self._forms Meta data"""
        request_data = request.POST if request.POST else None
        self.context = self._context_dict(self.context_template, request_data)