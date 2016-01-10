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

from django.forms import ModelForm, PasswordInput, Form, CharField, forms
from django.contrib.auth.models import User
from email import EmailTypes, Email
from django.contrib.auth import authenticate, login
from django.utils.translation import gettext_lazy as _

#
# Simple form for the registration - override the default widget for the Password field
#
class NewUserForm(ModelForm):
    """Form to create a new User - used in conjunction with the NewUserView class view"""
    class Meta:
        model = User
        fields = ['first_name','last_name','username','email','password']
        widgets = {'password': PasswordInput()}

    def __init__(self, *args, **kwargs):
        """Disable the help text"""
        super(NewUserForm, self).__init__(*args, **kwargs)
        self.fields['username'].help_text = None

    def save(self, commit=True):
        """ Customised save on the form, so that we can separate control and view """
        # If data is valid, proceeds to create a new post and redirect the user
        if self.is_valid():
            d = dict([(k,v) for k,v in self.cleaned_data.iteritems()])
            print d
            user = User.objects.create_user( **d )

            Email(EmailTypes.NewUserConfirmation).send(user)

            return user
        else:
            return None


class SignInForm(Form):
    """ Sign in form """
    username = CharField(strip=True, label=_('Username'), max_length = 30, required=True)
    password = CharField(strip=True, label=_('Password'), widget=PasswordInput(), required=True )

    def __init__(self, request=None, *args,**kwargs ):
        super(SignInForm,self).__init__(request, *args,**kwargs)
        self._request = request


    def clean(self):
        """Sub class cleaning to authenticate credentials"""
        super(SignInForm, self).clean()
        uname = self.cleaned_data['username']
        pword = self.cleaned_data['password']
        user = authenticate(username=uname, password=pword)
        if not user:
            raise forms.ValidationError(_("Unrecognised Username/Password combination - please correct and try again") )
        else:
            return self.cleaned_data

    def save(self, commit=True):
        """ Not a real save - but each form needs a save method for consistency"""
        if self.is_valid():
            uname = self.cleaned_data['username']
            pword = self.cleaned_data['password']

            user = authenticate(username=uname, password=pword)
            if not user:
                raise forms.ValidationError(_("Unrecognised Username/Password combination - please correct and try again") )
            else:
                login(self._request, user)
                return user
        else:
            return None