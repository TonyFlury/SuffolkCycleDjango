from django.shortcuts import render, redirect
from django.db.models import Count
from django.db.models.functions import Coalesce
from django.views.generic import View
from django.core.urlresolvers import reverse_lazy, reverse

import models
import forms

from stats.models import PageVisit

__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '11 Feb 2016'


# -----------------------------------------------------------------------------
#                               Change Log
#                               ----------
#
# 09-02-2016 : Issue 2: Implemented simple sponsorship list
# -----------------------------------------------------------------------------

def main(request):
    PageVisit.record(request)
    available = models.Opportunity.objects.filter(available=True, taken=False). \
        annotate(order_value=Coalesce('value', 'max_value')). \
        order_by('order_value')
    sponsors = models.Sponsor.objects.annotate(support_count=Count('supports')).filter(support_count__gt=0)

    return render(request, 'Sponsors/main.html', context={'sponsors': sponsors, 'available': available})


class interest(View):
    context = {'heading': 'Contact Details',
               'description': 'Thank you for your interest in sponsoring our {}.\n'
                              'Please complete the form, and we will contact you shortly.',
               'submit': 'Save',
               'appendix': 'Your contact details are only stored for the purposes of further communication about your '
                           'sponsorship offer. We will not use your details for any other purpose, and we will not '
                           'provide them to any 3rd party'}

    def get(self, request, opportunity_slug):
        opportunity = models.Opportunity.objects.get(slug=opportunity_slug)
        PageVisit.record(request, sub_document=opportunity.name)

        form = forms.Communications(initial={'opportunity': opportunity.id})
        context = self.context.copy()
        context['form'] = form
        context['description'] = context['description'].format(opportunity.name)
        return render(request, 'Sponsors/communicate.html', context=context)

    def post(self, request, opportunity_slug):
        if request.POST.get('confirmation', '') == 'True':
            return redirect('Sponsorship:Main')

        form = forms.Communications(request.POST)
        if form.is_valid():
            opportunity = models.Opportunity.objects.get(id=request.POST['opportunity'])
            sponsor = form.save()
            sponsor.potential = True
            sponsor.potentials.add(opportunity)
            sponsor.save()
            return render(request, 'Sponsors/communicate.html',
                          context={'opportunity': opportunity.id, 'confirmation': True})

        opportunity = models.Opportunity.objects.get(slug=opportunity_slug)
        context = self.context.copy()
        context['form'] = form
        context['description'] = context['description'].format(opportunity.name)
        return render(request, 'Sponsors/communicate.html',
                      context=context)
