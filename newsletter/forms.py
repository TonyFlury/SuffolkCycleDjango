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

from django.core.exceptions import ObjectDoesNotExist
from django.forms import Form, ModelForm, EmailField, HiddenInput
from models import NewsletterRecipient, Newsletter
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now


class NewsletterUnsubscribeForm(Form):
    email = EmailField()

    def clean(self):
        super(NewsletterUnsubscribeForm,self).clean()
        e = self.cleaned_data['email']
        try:
            c = NewsletterRecipient.objects.get(email = e)
        except ObjectDoesNotExist:
            self.add_error( 'email', _('{} isn''t subscribed to the Newsletter'.format(e)) )

        return self.cleaned_data

    def save(self, commit=True):
        if self.is_valid():
            print self.cleaned_data['email']
            nsu = NewsletterRecipient.objects.get(email = self.cleaned_data['email'])
            assert isinstance(nsu, NewsletterRecipient)
            d = nsu.delete()
            return self.cleaned_data['email']
        else:
            return None

class NewsletterSignUpForm(ModelForm):
    # noinspection PyClassicStyleClass
    class Meta:
        model = NewsletterRecipient
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            del kwargs['request']
        super(NewsletterSignUpForm, self).__init__(*args,**kwargs)

    def clean(self):
        return super(NewsletterSignUpForm,self).clean()

    def save(self, commit=True):
        return super(self.__class__, self).save(commit=commit)


class NewsletterUploadForm(ModelForm):
    # noinspection PyClassicStyleClass
    class Meta:
        model = Newsletter
        fields = ['title', 'content',]

    def clean(self):
        self.cleaned_data['pub_date'] = now()
        return self.cleaned_data