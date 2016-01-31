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

__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '23 Jan 2016'

from django.contrib.auth.models import User
from django import forms


class UserDetails(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = { 'first_name': forms.fields.TextInput(attrs={'size':15,'label':"First Name"}),
                    'last_name': forms.fields.TextInput(attrs={'size':15,'label':"Last Name"}),
                    'email': forms.fields.EmailInput(attrs={'size':30,'label':'Email'}), }
