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

from django.forms.forms import BaseForm

# Experimental mixin to provide the ability to easily define multiple forms on a single page
# Depends on a template being available to loop and render forms.
# Makes very few assumptions about the content of the template

class MultipleFormMixin(object):
    """ Multiple Form Mixin
        Looks for an Attribute named 'context_template' which is expected to be a dictionary.
        This dictionary is processed recursively (including any lists within the dictionary)
        If the value is a basic Form class, the value is replaced with a instatiated object of this class.
            If a key named 'prefix' exists within the same dictionary as a Form class, then the value is used as the prefix
            attrribute into the class instantiation - it is also retained as a tag

        Sets the following attributes :
            'self.context' = a fully interpreted set of values from 'context_template'
             'self.this_form' = the actual form which have been submitted based on the value of the submitted
        """

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
            if isinstance(item, type) and issubclass(item, BaseForm):
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

            if isinstance(v, type) and issubclass(v, BaseForm):
                form_tag, form_class = k, v
                continue

            if k == 'prefix':
                prefix = v

            result_dict[k] = v

        # Did we find a form : if so does this form need the request data ?
        if form_class and form_tag:

            if request_data and (result_dict['submit'] == request_data['submit']):
                result_dict[form_tag] = form_class(data=request_data, prefix = prefix or '')
                self.this_form = result_dict[form_tag]
            else:
                result_dict[form_tag] = form_class(prefix = prefix or '' )

        return result_dict

    def __init__(self, *args, **kwargs):

        if not hasattr(self, 'context_template'):
            raise AttributeError("'context_template' attribute must be defined")

        assert isinstance(self.context_template, dict)

        if not isinstance(self.context_template, dict):
            raise AttributeError("'context' attribute must be a dictionary")

        self.context, self.this_form = None, None

        super(MultipleFormMixin,self).__init__(*args,**kwargs)


    def get(self, request, *args, **kwargs):
        """ Set the self.forms and the self.this_form attributes based on the self._forms Meta data"""
        request_data = request.GET if request.GET else None
        self.context = self._context_dict(self.context_template, request_data)


    def post(self, request, *args, **kwargs):
        """ Set the self.forms and the self.this_form attributes based on the self._forms Meta data"""
        request_data = request.POST if request.POST else None
        self.context = self._context_dict(self.context_template, request_data)