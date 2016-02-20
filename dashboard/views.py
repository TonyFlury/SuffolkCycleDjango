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

from datetime import date, timedelta
from pprint import pprint

from django.http import HttpResponseServerError,HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy, reverse
from django.contrib.auth import login, authenticate

from stats.models import PageVisit

import forms

# Reuse the models and forms from the RegisteredUsers app to make password reset available
import RegisteredUsers.models
import RegisteredUsers.forms
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import cyclists.models

__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '23 Jan 2016'

# -----------------------------------------------------------------------------
#                               Change Log
#                               ----------
#
# 09-02-2016 : Issue 5: Change Password fails when passwords are different.
# -----------------------------------------------------------------------------


class UserDashboard(LoginRequiredMixin, View):
    """The Dashboard Page - will get a lot more complex - might need its own .py"""
    login_url = reverse_lazy("GetInvolved")

    def get(self, request):
        PageVisit.record(request)
        return render(request, "dashboard/pages/dashboard.html")


class MyDetails(LoginRequiredMixin, View):
    login_url = reverse_lazy("GetInvolved")

    context = {'heading': 'My Details',
               'description': 'Update your personal details here',
               'submit': ['Save', 'Change Password']}

    def get(self, request):

        context = self.context.copy()

        PageVisit.record(request)

        me = request.user
        form = forms.UserDetails(instance=me)

        context.update({'form': form})

        return render(request, 'dashboard/pages/dashboardPeople.html', context=context)

    def post(self, request):

        if request.POST['submit'] == 'Change Password':
            return redirect("Dashboard:PasswordReset")

        me = request.user
        form = forms.UserDetails(request.POST)
        context = self.context.copy()

        if form.is_valid():
            me.first_name, me.last_name, me.email = (form.cleaned_data[k] for k in ['first_name', 'last_name', 'email'])

            PageVisit.record(request, 'Details Changed')

            me.save()

            context.update({'description': 'Personal details saved',
                            'description_class': 'confirm',
                            'form': form})

            return render(request, 'dashboard/pages/dashboardPeople.html', context=context)

        context.update({'form': form})
        return render(request, 'dashboard/pages/dashboardPeople.html', context=context)


class PasswordReset(LoginRequiredMixin, View):
    context = {'heading': 'Change Password',
               'description': ' Enter your new password, and confirm',
               'submit': ['Change Now']}

    login_url = reverse_lazy("GetInvolved")

    def get(self, request):
        # Use the same mechanism as a 'forgotten password', but only have a 24 hour expiry period
        prr = RegisteredUsers.models.PasswordResetRequest.objects.create(user=request.user,
                                                                         expiry=date.today() + timedelta(days=1))
        form = RegisteredUsers.forms.PasswordReset(initial={'uuid': prr.uuid})

        context = self.context.copy()
        context['form'] = form

        return render(request, 'dashboard/pages/dashboard_PasswordChange.html', context=context)

    def post(self, request):

        if request.POST.get('confirmation','') == "True":
            return redirect('Dashboard:Home')

        form = RegisteredUsers.forms.PasswordReset(request.POST)

        if form.is_valid():
            user, pwd = form.save()

            user = authenticate(username=user.username, password=pwd)
            if user and user.is_active:
                login(request, user)
            else:
                return HttpResponseServerError("unable to re-authenticate user !!!!")

            PageVisit.record(request)

            return render(request, 'dashboard/pages/dashboard_PasswordChange.html', context={'confirmation':True})
        else:
            context = self.context.copy()
            context['form'] = form
            return render(request, 'dashboard/pages/dashboard_PasswordChange.html', context=context)


class CycleRoutes(LoginRequiredMixin, View):
    context = {'heading': 'Cycle Legs',
               'description': 'Click the tick box to choose the legs you are going to cycle',
               'top_submit': ['Save'],
               'submit': ['Save']}

    login_url = reverse_lazy("GetInvolved")

    def get(self, request):
        context = self.context.copy()

        cyclist = cyclists.models.Cyclist.objects.get(user=request.user)
        legs = cyclists.models.Leg.objects.order_by('date').extra(
                select={'cyclist_on_leg': "EXISTS(SELECT 1 FROM `cyclists_cyclist_legs` \
        WHERE `cyclists_cyclist_legs`.`leg_id` = `cyclists_leg`.id \
          AND `cyclists_cyclist_legs`.`cyclist_id` = %s)" % cyclist.id})

        context.update({'cyclists': cyclists,
                        'legs': legs})

        return render(request, 'dashboard/pages/dashboardCycleRoutes.html',
                      context=context)

    def post(self, request):
        pprint(request.POST)

        context = self.context.copy()

        cyclist = cyclists.models.Cyclist.objects.get(user=request.user)
        legs = cyclists.models.Leg.objects.order_by('date')

        for l in legs:
            if str(l.id) in request.POST.getlist('selected') and not cyclist.legs.filter(id=l.id).exists():
                cyclist.legs.add(l)
            elif str(l.id) not in request.POST.getlist('selected') and cyclist.legs.filter(id=l.id).exists():
                cyclist.legs.remove(l)

        cyclist.save()

        legs = cyclists.models.Leg.objects.order_by('date').extra(
                select={'cyclist_on_leg': "EXISTS(SELECT 1 FROM `cyclists_cyclist_legs` \
                        WHERE `cyclists_cyclist_legs`.`leg_id` = `cyclists_leg`.id \
                        AND `cyclists_cyclist_legs`.`cyclist_id` = %s)" % cyclist.id})

        context.update({'cyclists': cyclists,
                        'legs': legs})

        return render(request, 'dashboard/pages/dashboardCycleRoutes.html',
                      context=context)


class OtherVolunteering(View):
    pass


class Fundraising(View):
    pass
