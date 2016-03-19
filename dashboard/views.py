#!/usr/bin/env python
"""
# SuffolkCycleDjango : Implementation of test_03_views.py - separate for compartmentalisation

Summary : 
    <summary of module/class being implemented>
Use Case : 
    As a <actor> I want <outcome> So that <justification>

Testable Statements :
    Can I <Boolean statement>
    ....
"""
import logging
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from datetime import date, timedelta
from django.http import HttpResponseServerError
from django.shortcuts import render, redirect
from django.views.generic import View
from django.core.urlresolvers import reverse_lazy, reverse
from django.contrib.auth import login, authenticate
from django.db.models import Case, When, Value
from django.db.models import IntegerField
from django.utils.http import urlencode
from urllib import quote


from stats.models import PageVisit

import forms

# Reuse the models and forms from the RegisteredUsers app to make password reset available
import RegisteredUsers.models
import RegisteredUsers.forms
import cyclists.models

from PIL import Image

from StringIO import StringIO

__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '23 Jan 2016'


class NoDashboard(PermissionDenied):
    """Short Hand exception for when staff try to use the Dashboard"""
    def __init__(self, *args, **kwargs):
        super(NoDashboard,self).__init__('Only cyclists have Dashboards', )

# -----------------------------------------------------------------------------
#                               Change Log
#                               ----------
#
# 09-02-2016 : Issue 5: Change Password fails when passwords are different.
# -----------------------------------------------------------------------------


class UserDashboard(View):
    """The Dashboard Page"""
    def get(self, request):
        if not request.user.is_authenticated():
            logging.warning('Unauthorised attempt to access dashboard')
            return redirect( reverse("GetInvolved"))

        try:
            cyclist = cyclists.models.Cyclist.objects.get(user = request.user)
        except ObjectDoesNotExist:
            raise NoDashboard()

        progress = sum( (1 if getattr(cyclist, attr_name) else 0) for attr_name in
                        ['picture', 'statement', 'fundraising_site', 'targetAmount'] )

        if cyclist.legs.all():
            progress += 1

        PageVisit.record(request)
        return render(request, "dashboard/pages/dashboard.html",
                      context={'cyclist': cyclist, 'progress': {'count':progress, 'limit':5}})

class MyDetails(View):
    context = {'heading': 'My Details',
               'description': 'Update your personal details here',
                'form_enctype': 'enctype="multipart/form-data"',
               'submit': ['Save', 'Change Password']}

    def get(self, request):
        if not request.user.is_authenticated():
            logging.warning('Unauthorised attempt to access dashboard')
            return redirect( reverse("GetInvolved"))

        context = self.context.copy()

        PageVisit.record(request)

        me = request.user
        try:
            cyclist = cyclists.models.Cyclist.objects.get(user = me)
        except ObjectDoesNotExist:
            raise NoDashboard()

        form = forms.MyDetails(instance=[me,cyclist])

        context['form'] = form
        context['cyclist'] = cyclist

        return render(request, 'dashboard/pages/MyDetails.html', context=context)

    def post(self, request):
        if not request.user.is_authenticated():
            logging.warning('Unauthorised attempt to access dashboard')
            return redirect( reverse("GetInvolved"))

        if request.POST.get('confirmation',''):
            return redirect(reverse('Dashboard:MyDetails'))

        if request.POST['submit'] == 'Change Password':
            return redirect("Dashboard:PasswordReset")

        me = request.user
        try:
            cyclist = cyclists.models.Cyclist.objects.get(user = me)
        except:
            raise NoDashboard()

        form = forms.MyDetails(instance=[me,cyclist], data=request.POST, files=request.FILES)
        context = self.context.copy()

        if form.is_valid():

            PageVisit.record(request, 'Details Changed')

            for k in ['first_name','last_name', 'email']:
                if form.cleaned_data[k] != getattr(me, k):
                    setattr(me, k, form.cleaned_data[k])
            me.save()

            if 'picture-clear' in form.cleaned_data:
                cyclist.picture = ''
            else:
                if form.cleaned_data['picture'] != cyclist.picture:
                    cyclist.picture = form.cleaned_data['picture']
            cyclist.save()

            return render(request, 'dashboard/pages/MyDetails.html',
                          context={'confirmation': {'title':'Personal details saved',
                                 'message': 'Your changes have been saved. Click OK to return to your dashboard'}})

        context['form'] =  form
        context['cyclist'] = cyclist
        return render(request, 'dashboard/pages/MyDetails.html', context=context )


class PasswordReset(View):
    context = {'heading': 'Change Password',
               'description': ' Enter your new password, and confirm',
               'submit': ['Change Now']}

    def get(self, request):
        if not request.user.is_authenticated():
            logging.warning('Unauthorised attempt to access dashboard')
            return redirect( reverse("GetInvolved"))

        try:
            cyclist = cyclists.models.Cyclist.objects.get(user = request.user)
        except ObjectDoesNotExist:
            raise NoDashboard()

        # Use the same mechanism as a 'forgotten password', but only have a 24 hour expiry period
        prr = RegisteredUsers.models.PasswordResetRequest.objects.create(user=request.user,
                                                                         expiry=date.today() + timedelta(days=1))
        form = RegisteredUsers.forms.PasswordReset(initial={'uuid': prr.uuid})

        context = self.context.copy()
        context['form'] = form

        return render(request, 'dashboard/pages/PasswordChange.html', context=context)

    def post(self, request):
        if not request.user.is_authenticated():
            logging.warning('Unauthorised attempt to access dashboard')
            return redirect( reverse("GetInvolved"))

        try:
            cyclist = cyclists.models.Cyclist.objects.get(user = request.user)
        except ObjectDoesNotExist:
            raise NoDashboard()

        if request.POST.get('confirmation',''):
            return redirect('Dashboard:MyDetails')

        form = RegisteredUsers.forms.PasswordReset(request.POST)

        if form.is_valid():
            user, pwd = form.save()

            user = authenticate(username=user.username, password=pwd)
            if user and user.is_active:
                login(request, user)
            else:
                return HttpResponseServerError("unable to re-authenticate user !!!!")

            PageVisit.record(request)

            return render(request, 'dashboard/pages/PasswordChange.html',
                          context={'confirmation': {'title':'Password Changed',
                                 'message': 'Your new password has been saved. Click OK to return to your dashboard'}})
        else:
            context = self.context.copy()
            context['form'] = form
            return render(request, 'dashboard/pages/PasswordChange.html', context=context)


class CycleRoutes(View):
    context = {'heading': 'Cycle Route : Legs',
               'description': 'Click the tick box to choose the legs you are going to cycle',
               'top_submit': ['Save'],
               'submit': ['Save']}

    @staticmethod
    def get_legs(cyclist_inst):
        """Retrieve an annotated list of all the legs - marked with a Boolean if the given cyclists has selected them"""
        my_legs = cyclist_inst.legs.all().values_list('pk',flat=True)
        return cyclists.models.Leg.objects.annotate( cyclist_on_leg=Case(
                                                            When(id__in=my_legs, then=Value('1')),
                                                            default=Value('0'),
                                                            output_field=IntegerField() )).order_by('date','-morning')


    def get(self, request):
        if not request.user.is_authenticated():
            logging.warning('Unauthorised attempt to access dashboard')
            return redirect( reverse("GetInvolved"))

        context = self.context.copy()

        try:
            cyclist = cyclists.models.Cyclist.objects.get(user = request.user)
        except ObjectDoesNotExist:
            raise NoDashboard()

        # Custom Query to select all the legs and add a Boolean where the cyclist has selected that leg already
        # Looked for ways to do this

        # Fetch a simple list of all the legs this cyclist is on
        context['legs'] = self.get_legs( cyclist )

        return render(request, 'dashboard/pages/CycleRoutes.html',
                      context=context)

    def post(self, request):
        if not request.user.is_authenticated():
            logging.warning('Unauthorised attempt to access dashboard')
            return redirect( reverse("GetInvolved"))

        if request.POST.get('confirmation',''):
            return redirect(reverse('Dashboard:CycleRoutes'))

        context = self.context.copy()

        try:
            cyclist = cyclists.models.Cyclist.objects.get(user = request.user)
        except ObjectDoesNotExist:
            raise NoDashboard()

        all_legs = cyclists.models.Leg.objects.order_by('date')

        # Unlike many other forms, there is nothing to validate here
        # All that the user has to do is tick/untick checkboxes - and it is allowed to have none ticked.

        # No need to worry if the legs are already added or not - adding something twice has no effect
        for l in all_legs:
            getattr(cyclist.legs,'add' if str(l.id) in request.POST.getlist('selected') else 'remove')(l)

        return render(request, 'dashboard/pages/CycleRoutes.html',
                          context={'confirmation': {'title':'Selection Saved',
                                 'message': 'Your selection has saved. Click OK to return to your dashboard'}})


class OtherVolunteering(View):
    pass


class Fundraising(View):
    context = {'heading': 'Fundraising Details',
               'description': 'The details of your current Fundriaising',
               'submit': ['Save']}

    def get(self, request):

        if not request.user.is_authenticated():
            logging.warning('Unauthorised attempt to access dashboard')
            return redirect( reverse("GetInvolved"))

        try:
            cyclist = cyclists.models.Cyclist.objects.get(user = request.user)
        except ObjectDoesNotExist:
            raise NoDashboard()

        context = self.context.copy()
        context['form'] = forms.FundRaising(instance=cyclist)
        context['cyclist'] = cyclist

        return render(request, 'dashboard/pages/FundRaising.html', context=context)

    def post(self, request):
        if not request.user.is_authenticated():
            logging.warning('Unauthorised attempt to access dashboard')
            return redirect( reverse("GetInvolved"))

        if request.POST.get('confirmation',''):
            return redirect(reverse('Dashboard:FundRaising'))

        try:
            cyclist = cyclists.models.Cyclist.objects.get(user = request.user)
        except ObjectDoesNotExist:
            raise NoDashboard()

        form = forms.FundRaising(instance=cyclist, data=request.POST)

        if form.is_valid():
            form.save()

            return render(request, 'dashboard/pages/FundRaising.html',
                          context={'confirmation': {'title':'Information Saved',
                                 'message': 'Your changes haved been saved. Click OK to return to your dashboard'}})
        else:
            cyclist = cyclists.models.Cyclist.objects.get(user=request.user)
            context = self.context.copy()
            context['form'] = form
            context['cyclist'] = cyclist

            return render(request, 'dashboard/pages/FundRaising.html', context=context)

class FundMe(View):
    def get(self, request):
        if not request.user.is_authenticated():
            logging.warning('Unauthorised attempt to access dashboard')
            return redirect( reverse("GetInvolved"))

        try:
            cyclist = cyclists.models.Cyclist.objects.get(user = request.user)
        except ObjectDoesNotExist:
            raise NoDashboard()

        local_url = reverse('FundMe',kwargs={'username':request.user.username})
        full_url = '{protocol}{host}{page}'.format(
                                                protocol='http://',
                                                host = request.get_host(),
                                                page = local_url)

        facebookurl = "https://www.facebook.com/dialog/feed?" \
                      "app_id=1695226697422284" \
                      "&amp;display=popup" \
                      "&amp;caption={ title }" \
                      "&amp;link={ link }" \
                      "&amp;redirect_uri={ redirect }".format(
                title = quote('Support {} on the Great Suffolk Cycle Ride'.format(request.user.get_full_name()),''),
                link = quote( full_url, ''),
                redirect = quote( full_url, '') )

        twitterurl = "http://twitter.com/intent/tweet?{data}".format(
                        data = urlencode( {'status':'Support {name} on the Great Suffolk Cycle Ride\n{url}'.format(
                                                name=request.user.get_full_name(),
                                                url=full_url) } )
                                        )

        return render(request, 'SuffolkCycleRide/pages/fundme.html',
                    context={'cyclist':cyclist,
                             'mockup':{'local_url': local_url,
                                       'full_url': full_url,
                                       'urls':{ 'facebook': facebookurl,
                                                'twitter': twitterurl }}
                             } )

    def post(self, request):
        pass