#!/usr/bin/env python
"""
# SuffolkCycle : Implementation of forms.py

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
__created__ = '07 Jan 2016'

from django.forms import ModelForm
from models import NewsletterSignUp

class NewsletterSignUpForm(ModelForm):
    class Meta:
        model = NewsletterSignUp
        fields = '__all__'

    def save(self, commit=True):
        print "{} save : Saving".format(self.__class__)
        super(self.__class__, self).save(commit=commit)