#!/usr/bin/env python
"""
# SuffolkCycleDjango : Implementation of forms.py

Summary : 
    <summary of module/class being implemented>
Use Case : 
    As a <actor> I want <outcome> So that <justification>

Testable Statements :
    Can I <Boolean statement>
    ....
"""

from django import forms
from django.core import exceptions
from django.utils.text import slugify

import models

__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '13 Feb 2016'


class Communications(forms.ModelForm):
    opportunity = forms.IntegerField()

    # noinspection PyClassicStyleClass
    class Meta:
        model = models.Sponsor
        fields = ['name','company_name', 'email','telephone','mobile', 'communication_preference']
        labels = { 'company_name':'Company Name',
                   'communication_preference': 'Pref. contact method',
                  'telephone':'Tel number',
                  'mobile':'Mobile number'}
        widgets = {'communication_preference': forms.RadioSelect(),
                   'mobile':forms.TextInput(attrs={ 'type':'tel',
                                                        'pattern':'[0-9]{11}'} ),
                   'telephone':forms.TextInput(attrs={ 'type':'tel',
                                                        'pattern':'[0-9]{11}'} ) }
        error_messages = {'name':{'required':'Please provide your name'},
                          'communication_preference':{'required':'You must select your preferred communication method'}}

    def __init__(self, *args, **kwargs):
        super(Communications, self).__init__(*args, **kwargs)
        self.fields['opportunity'].widget = self.fields['opportunity'].hidden_widget()

    def clean(self):
        email, telephone, mobile = self.cleaned_data.get('email',None), \
                                   self.cleaned_data.get('telephone',None),\
                                   self.cleaned_data.get('mobile',None)
        preference = self.cleaned_data.get('communication_preference',None)

        if not(email or telephone or mobile):
            raise exceptions.ValidationError(
                            'You must provide at least an email address, telephone number or mobile phone number',
                            code='invalid',)

        # Next two checks will only fail on browsers without Javascript enabled
        if not preference:
            raise exceptions.ValidationError(
                            "You must select your preferred communication method",
                            code='invalid',)

        if not self.cleaned_data.get(preference,None):
            raise exceptions.ValidationError(
                            "'%(method)s' selected as your preferred contact method, but %(name)s not provided",
                            code='invalid',
                            params={'method': preference,
                                    'name': preference + " address" if preference == 'email' else
                                            preference + " number"
                                    })
        return self.cleaned_data


    def save(self, commit=True):
        comms = super(Communications, self).save( commit=False)
        comms.slug = slugify(comms.name)
        if commit:
            comms.save( )
        return comms