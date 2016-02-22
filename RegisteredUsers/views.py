from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import login, authenticate
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
from django.shortcuts import render, redirect
from django.views.generic import View
from django.core.urlresolvers import reverse_lazy, reverse
from django.contrib.auth import logout

from stats.models import PageVisit
from EmailPlus.email import Email

import forms
import models

from datetime import date as dt
import uuid

__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '09 Feb 2016'


# -----------------------------------------------------------------------------
#                               Change Log
#                               ----------
#
# 09-02-2016 : Issue 1: Signin (and SignOut) fails due to incorrect URL resolution.
# 09-02-2016 : Issue 12 : Password Reset form fails due to incorrect response page.
# -----------------------------------------------------------------------------



class SignIn(View):
    """ Sign in On via a simple form """

    # Single store for Form information re-used in GET and Post
    context = {'heading': "Sign In",
               'description': 'Enter your username and password',
               'submit': "Sign In",
               'ResetUrl': reverse_lazy('User:ResetRequest')
               }

    # noinspection PyIncorrectDocstring
    def get(self, request):
        """ Initial fetch of SignIn Form - Nothing to go wrong here"""
        c = self.context.copy()
        c['form'] = forms.SignInForm()
        return render(request, "RegisteredUsers/pages/SignIn.html",
                      context=c)

    # noinspection PyIncorrectDocstring
    def post(self, request):
        """ Process the Form contents """

        c = self.context.copy()
        form = forms.SignInForm(request.POST)

        # Is the form filled in correctly - including is it a valid username/password combo
        if form.is_valid():
            # This form.save logs the user in, and therefore needs the request as well as the form, and record this
            form.save(request=request)

            PageVisit.record(request)
            return HttpResponseRedirect(reverse("Home"))

        # If we get here we have errors
        c['form'] = form
        return render(request, "RegisteredUsers/pages/SignIn.html", context=c)


# noinspection PyPep8Naming,PyIncorrectDocstring
def SignOut(request):
    """ A simple view - No form, no complexity - just logout and pop the user back home """
    logout(request=request)
    return HttpResponseRedirect(reverse("Home"), {})


class ResetRequestView(View):
    """ view used for a user to request a password reset

        the form prompts for email address - and finds the relevant user
    """
    context = {'heading': "Request a Password Reset",
               'description': 'Enter your email address',
               'submit': "Request a Reset"
               }

    def get(self, request):
        c = self.context.copy()
        c['form'] = forms.PasswordResetRequest()
        return render(request, "base/SingleForm.html", context=c)

    def post(self, request):
        c = self.context.copy()
        form = forms.PasswordResetRequest(request.POST)
        if form.is_valid():

            # The save form creates an instance of the PasswordResetRequestModel: expiry date is 14 days from 'today'
            reset = form.save()
            reset_local = reverse('User:Reset', args=[str(reset.uuid)])

            # Send the email to the identified user: Email contains a URL unique to that reset (128 bit UUID)
            Email(subject="Great Suffolk Cycle Ride : Password reset",
                  body=render_to_string("RegisteredUsers/Email/PasswordResetRequest.txt",
                                        context={'user': reset.user,
                                                 'ResetUrl': request.build_absolute_uri(reset_local),
                                                 'ExpireBy': reset.expiry,
                                                 'HOST': request.get_host()
                                                 })
                  ).send(reset.user.email)

            # This will record the page visit - but not who requested the reset - only record a successful attempt
            # Pop the user to the ResetConfirmation page
            PageVisit.record(request)
            return render(request, "RegisteredUsers/pages/ResetConfirmed.html",
                          context={
                              'email': reset.user.email,
                              'expiry': dt.strftime(reset.expiry, "%d %b %Y")
                          })
        else:
            # Remder the form with any errors
            c['form'] = form
            return render(request, "base/SingleForm.html", context=c)


class Reset(View):
    context = {'heading': "New Password",
               'description': 'Enter and confirm your new password',
               'submit': "Reset Password",
               'action': ''
               }

    def get(self, request, reset_uuid):

        try:
            prr = models.PasswordResetRequest.objects.get(uuid=uuid.UUID(reset_uuid))
        except ObjectDoesNotExist:
            return render(request, "RegisteredUsers/pages/UnknownReset.html")

        if prr.expiry < dt.today():
            return render(request, "RegisteredUsers/pages/UnknownReset.html")

        form = forms.PasswordReset(initial={'uuid': reset_uuid})

        c = self.context.copy()
        c['form'] = form

        return render(request,
                      "RegisteredUsers/pages/PasswordChange.html",
                      context=c)

    def post(self, request, reset_uuid):

        if request.POST.get('confirmation','') == "True":
            return redirect('Home')

        form = forms.PasswordReset(request.POST)
        if form.is_valid():
            user, pwd = form.save()
            user = authenticate(username=user.username, password=pwd)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return render(request,
                            "RegisteredUsers/pages/PasswordChange.html",
                            context={'confirmation':True})
                else:
                    return render(request, "pages/Invalid.html")
            else:
                return render(request, "pages/Incorrect.html")
        else:
            c = self.context.copy()
            c['form'] = form
            return render(request,
                          "RegisteredUsers/pages/PasswordChange.html",
                          context=c)
