#!/usr/bin/env python
# coding=utf-8
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
from datetime import date, timedelta

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from django import forms

import models

__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '07 Jan 2016'


class NewUserForm(forms.ModelForm):
    """ Form to create a new User
       Preferred rather than any builtin registration form
    """
    confirm_password = forms.CharField(max_length=None, label='Confirm Password', required=True,
                                       widget=forms.PasswordInput(attrs={'required': True}),
                                       error_messages={'required': 'You must re-enter the password'})

    # noinspection PyClassicStyleClass
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password', 'confirm_password']
        widgets = {'password': forms.PasswordInput(attrs={'required': True}),
                   'email': forms.fields.EmailInput(attrs={'required': True})}
        error_messages = {'email': {'required': 'You must provide an email address'},
                          'username': {'required': 'You must provide a username'},
                          'password': {'required': 'You must provide a password'},
                          'confirm_password': {'required': 'You must re-enter the password'}}

    def __init__(self, *args, **kwargs):
        """Disable the help text"""
        super(NewUserForm, self).__init__(*args, **kwargs)
        self.fields['username'].help_text = None
        self.fields['password'].required = True

    def clean(self):
        super(NewUserForm, self).clean()

        if not (self.cleaned_data['first_name'] and self.cleaned_data['last_name']):
            field = 'first_name'
            field = 'last_name' if self.cleaned_data[field] else field
            self.add_error(field, 'You must provide both your first and last name')
            return None

        if ('password' not in self.cleaned_data) or ('confirm_password' not in self.cleaned_data):
            return self.cleaned_data

        if not (self.cleaned_data['password'] == self.cleaned_data['confirm_password']):
            self.add_error('confirm_password', 'Passwords do not match')
            return None

        return self.cleaned_data

    def clean_username(self):
        try:
            User.objects.get(username=self.cleaned_data['username'])
        except ObjectDoesNotExist:
            return self.cleaned_data['username']

        raise forms.ValidationError("Username already in use")

    def clean_email(self):
        if not self.cleaned_data['email']:
            self.add_error('email', 'You must provide an email address')
            return None

        try:
            User.objects.get(email=self.cleaned_data['email'])
        except ObjectDoesNotExist:
            return self.cleaned_data['email']

        raise forms.ValidationError("Email address already in use")

    # noinspection PyIncorrectDocstring
    def save(self, commit=True):
        """ Customised save on the form, so that we can separate control and view """

        # Fugly code - tidy - Explicit is better
        if self.is_valid():
            d = dict([(k, v) for k, v in self.cleaned_data.iteritems() if k != 'confirm_password'])
            user = User.objects.create_user(**d)
            return user
        else:
            return None

    # noinspection PyIncorrectDocstring
    def login(self, request):
        """ Helper method to prevent login code in more than one place """
        user = authenticate(username=self.cleaned_data['username'], password=self.cleaned_data['password'])
        login(request, user)


class SignInForm(forms.Form):
    """ Sign in form - used rather that trying to re-style the normal admin provided SignIn Form"""
    username = forms.fields.CharField(strip=True,
                                      label=_('Username'),
                                      error_messages={'required': 'Username is required'},
                                      max_length=30, required=True)
    password = forms.fields.CharField(label=_('Password'), widget=forms.PasswordInput(),
                                      error_messages={'required': 'Password is required'},
                                      required=True)

    def clean(self):
        """Sub class clean method to allow authenticate of credentials
            i.e. the form is valid if the username and password are a correct combination
        """
        cleaned_data = super(SignInForm, self).clean()

        if 'username' not in cleaned_data:
            return cleaned_data

        if 'password' not in cleaned_data:
            return cleaned_data

        uname = cleaned_data['username']
        pword = cleaned_data['password']
        user = authenticate(username=uname, password=pword)
        if not user:
            raise forms.ValidationError(_("Unrecognised Username/Password combination - please correct and try again"))
        else:
            return cleaned_data

    # noinspection PyIncorrectDocstring
    def save(self, request=None):
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
    email = forms.fields.CharField(label=_('Email'), widget=forms.fields.EmailInput(), required=True,
                                   error_messages={'required': 'Enter your email address'})

    def __init__(self, *args, **kwargs):
        super(PasswordResetRequest, self).__init__(*args, **kwargs)

    def clean(self):
        super(PasswordResetRequest, self).clean()
        if 'email' not in self.cleaned_data:
            return self.cleaned_data

        e = self.cleaned_data['email']
        try:
            User.objects.get(email=e)
        except ObjectDoesNotExist:
            self.add_error('email', _("Email '{}' is not registered on this system".format(e)))

    def save(self):
        e = self.cleaned_data['email']
        user = User.objects.get(email=e)
        prr = models.PasswordResetRequest.objects.create(user=user, expiry=date.today() + timedelta(days=14))
        prr.save()
        return prr


class PasswordReset(forms.Form):
    newPassword = forms.fields.CharField(label=_('New Password'), widget=forms.PasswordInput(), required=True)
    confirmPassword = forms.fields.CharField(strip=True, label=_('Confirm Password'), widget=forms.PasswordInput(),
                                             required=True)
    uuid = forms.fields.UUIDField()

    def __init__(self, *args, **kwargs):
        super(PasswordReset, self).__init__(*args, **kwargs)
        self.fields['uuid'].widget = self.fields['uuid'].hidden_widget()

    def clean(self):
        if 'newPassword' not in self.cleaned_data or 'confirmPassword' not in self.cleaned_data:
            return self.cleaned_data

        if self.cleaned_data['newPassword'] != self.cleaned_data['confirmPassword']:
            self.add_error('newPassword', _('Passwords don''t match'))
        else:
            return self.cleaned_data

    def save(self):
        prr = models.PasswordResetRequest.objects.get(uuid=self.cleaned_data['uuid'])
        u = prr.user
        pwd = self.cleaned_data['newPassword']
        u.set_password(pwd)
        u.save()
        prr.delete()
        return u, pwd
