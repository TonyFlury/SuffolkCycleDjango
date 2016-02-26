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

__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '22 Feb 2016'


class ContactChoices(object):
    choices = { 'volunteering':'I would like to offer to help',
                 'participating':'I have a question about participating as a cyclist',
                 'website':'I have a problem with the website',
                 'sponsorship':'I am interested in sponsoring part of the event',
                 'donation':'I want to make a donation',
                 'something else':'Something else not covered in the list' }
    @classmethod
    def choiceList(cls):
        return [(k,v) for k,v in cls.choices.iteritems()]

    @classmethod
    def fullVersion(cls, reason):
        return cls.choices.get(reason,None)

class ContactUs(forms.Form):
    sender_email = forms.EmailField(label='Your email', required=True)
    sender_name = forms.CharField(max_length=120, label='Your name', required=True)
    reason = forms.ChoiceField( required=True,
                                label='Your reason for contacting us',
                                choices = ContactChoices.choiceList() )
    content = forms.CharField(required=True, widget=forms.Textarea(attrs={'cols':40, 'rows':10}), max_length=800)

