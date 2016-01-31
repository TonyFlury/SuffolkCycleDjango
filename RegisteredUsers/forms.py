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

from datetime import date, timedelta

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from django import forms

import models

class NewUserForm(forms.ModelForm):
    """ Form to create a new User
       Preferred rather than any builtin registration form
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password']
        widgets = {'password': forms.PasswordInput(attrs={'required': True}),
                   'email': forms.fields.EmailInput(attrs={'required': True})}

    def __init__(self, *args, **kwargs):
        """Disable the help text"""

        self._request = kwargs.get('request', None)
        if 'request' in kwargs:
            del kwargs['request']

        super(NewUserForm, self).__init__(*args, **kwargs)
        self.fields['username'].help_text = None

    def clean_username(self):
        try:
            unique = User.objects.get(username=self.cleaned_data['username'])
        except ObjectDoesNotExist:
            return self.cleaned_data['username']

        raise forms.ValidationError("Username already in use")

    def clean_email(self):
        try:
            unique = User.objects.get(email=self.cleaned_data['email'])
        except ObjectDoesNotExist:
            return self.cleaned_data['email']

        raise forms.ValidationError("Email address already in use")


    def save(self, commit=True):
        """ Customised save on the form, so that we can separate control and view """

        # Fugly code - tidy - Explicit is better
        if self.is_valid():
            d = dict([(k, v) for k, v in self.cleaned_data.iteritems()])
            user = User.objects.create_user(**d)
            return user
        else:
            return None

    def login(self, request):
        """ Helper method to prevent login code in more than one place """
        user = authenticate( username=self.cleaned_data['username'], password=self.cleaned_data['password'] )
        login(request, user)


class SignInForm(forms.Form):
    """ Sign in form - used rather that trying to re-style the normal admin provided SignIn Form"""
    username = forms.fields.CharField(strip=True, label=_('Username'), max_length=30, required=True)
    password = forms.fields.CharField(strip=True, label=_('Password'), widget=forms.PasswordInput(), required=True)

    def __init__(self, request=None, *args, **kwargs):
        super(SignInForm, self).__init__(request, *args, **kwargs)
        self._request = request

    def clean(self):
        """Sub class clean method to allow authenticate of credentials
            i.e. the form is valid if the username and password are a correct combination
        """
        super(SignInForm, self).clean()
        uname = self.cleaned_data['username']
        pword = self.cleaned_data['password']
        user = authenticate(username=uname, password=pword)
        if not user:
            raise forms.ValidationError(_("Unrecognised Username/Password combination - please correct and try again"))
        else:
            return self.cleaned_data

    def save(self, commit=True, request = None):
        """ Not a real save - but each form needs a save method for consistency
            Make the view simple by overriding the save method and making it a login method.
        """
        if self.is_valid():
            uname = self.cleaned_data['username']
            pword = self.cleaned_data['password']

            user = authenticate(username=uname, password=pword)
            if not user:
                raise forms.ValidationError(
                        _("Unrecognised Username/Password combination - please correct and try again"))
            else:
                login(request, user)
                return user
        else:
            return None


class PasswordResetRequest(forms.Form):
    """ Form to allow a user to request a Password Reset - identify the user via email address.

        User creation process ensures that email is unique.
    """
    email = forms.fields.CharField(strip=True, label=_('Email'), widget=forms.fields.EmailInput(), required=True)

    def __init__(self, request=None, *args, **kwargs):
        super(PasswordResetRequest, self).__init__(request, *args, **kwargs)

    def clean(self):
        super(PasswordResetRequest, self).clean()
        e = self.cleaned_data['email']
        try:
            c = User.objects.get(email=e)
        except ObjectDoesNotExist:
            self.add_error('email', _('{} is not registered on this system'.format(e)))

    def save(self):
        e = self.cleaned_data['email']
        user = User.objects.get(email=e)
        prr = models.PasswordResetRequest.objects.create(user=user, expiry=date.today() + timedelta(days=14))
        prr.save()
        return prr


class PasswordReset(forms.Form):
    newPassword = forms.fields.CharField(strip=True, label=_('New Password'), widget=forms.PasswordInput(), required=True)
    confirmPassword = forms.fields.CharField(strip=True, label=_('New Password'), widget=forms.PasswordInput(), required=True)
    uuid = forms.fields.UUIDField()

    def __init__(self, *args, **kwargs):
        super(PasswordReset, self).__init__(*args, **kwargs)
        self.fields['uuid'].widget = self.fields['uuid'].hidden_widget()

    def clean(self):
        if self.cleaned_data.get('newPassword','') != self.cleaned_data.get('confirmPassword','') :
            self.add_error('email', _('Passwords don''t match'))
        else:
            return self.cleaned_data

    def save(self):
        prr = models.PasswordResetRequest.objects.get(uuid=self.cleaned_data['uuid'])
        u = prr.user
        pwd = self.cleaned_data['newPassword']
        u.set_password( pwd)
        u.save()
        prr.delete()
        return u, pwd
