import logging
from django.core.exceptions import SuspiciousOperation
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.conf import settings

from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.views.generic import View
from django.core.urlresolvers import reverse

from newsletter.forms import NewsletterSignUpForm
from RegisteredUsers.forms import NewUserForm
from newsletter.models import Newsletter
from stats.models import PageVisit
from django.core.mail import send_mail

from EnhancedForms import MultipleFormMixin

from context_processor import settings_base_url
import forms

import cyclists.models


# noinspection PyIncorrectDocstring
def home(request):
    """ The front page - where everybody first lands"""
    PageVisit.record(request)

    funds = cyclists.models.Cyclist.total_funds()
    if funds['target'] and funds['pledges']:
        funds['target'] = max(2000, funds['target'])
        funds['percentage'] = round(100*funds['pledges']/funds['target'])
    else:
        funds = {}

    return render(request, "SuffolkCycleRide/pages/home.html", context={
            'funding':{'pledges':"{:.0f}".format(funds['pledges']),
                       'target':"{:.0f}".format(funds['target']),
                       'percentage':"{:.0f}".format(funds['percentage']) } if funds else {} } )

def the_event(request):
    """The Event page - with a summary of the event"""
    PageVisit.record(request)

    legs = cyclists.models.Leg.objects.all().order_by('date','-morning')

    if legs:
        stats = cyclists.models.Leg.Totals()
        first_leg = legs[0]
        last_leg = cyclists.models.Leg.objects.all().order_by('-date','morning')[0]
    else:
        stats = {}
        first_leg = None
        last_leg = None

    return render(request, "SuffolkCycleRide/pages/theevent.html", context={'event':{ 'stats':stats,
                                                                                       'legs':legs,
                                                                                      'first_leg':first_leg,
                                                                                      'last_leg':last_leg }})

def sunrise(request):
    return render(request, "SuffolkCycleRide/pages/sunrise.html")
#To Implmenent Sunrise Fundraising Page - and url entry for it.

# noinspection PyIncorrectDocstring
def privacy(request):
    """The Read more page - a list of the newsletter posts"""
    PageVisit.record(request)
    return render(request, "SuffolkCycleRide/pages/privacy.html")


class GetInvolved(MultipleFormMixin, View):
    """Multiple form page - Newsletter Subscription, and New User Registration"""
    context_template = {
                'title': 'The Great Suffolk Cycle Ride 2016 : Get Involved',
                'forms': [
                    { 'name': 'Newsletter Sign Up',
                      'description': 'Do you want to keep informed, but not ready to sign up to take part. Then our newsletter is ideal for you.',
                      'form': NewsletterSignUpForm,
                      'submit': u'Send me the newsletter',
                      'prefix': 'nl' },
                    { 'name': 'Registration',
                      'description': 'Create an account here - your first step to participating or volunteering',
                      'form': NewUserForm,
                      'submit': u'Register',
                      'prefix': 'r'},
                    ]
                }

    def get(self, request):
        super(GetInvolved, self).get(request)

        PageVisit.record(request)

        return render(request, "base/VerticalForm.html", context=self.context )

    def post(self, request):

        super(GetInvolved, self).post(request)

        if self.this_form.is_valid():

            if self.this_form.prefix == 'nl':
                PageVisit.record(request, sub_document='Newsletter SignUp')
                sub = self.this_form.save()

                return render( request, "newsletter/pages/subscription_confirmation.html",
                               context = {'email': sub.email })

            if self.this_form.prefix == 'r':
                PageVisit.record(request, sub_document='New User Reqistration')
                user = self.this_form.save()
                send_mail( from_email = settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[ user.email ],
                            subject="Welcome to the Great Suffolk Cycle Ride",
                            message=render_to_string( "RegisteredUsers/Email/NewUserConfirmation.txt",
                                    context=dict( {'user': user,
                                             'ResetUrl': request.build_absolute_uri( reverse("User:ResetRequest") ),
                                             'HOST': request.get_host() }.items() +\
                                             settings_base_url(request).items()
                                             )))
                self.this_form.login(request)
                logging.info('Successful Registration')
                return HttpResponseRedirect( reverse('Dashboard:Home') )

        return render(request, "base/VerticalForm.html", context=self.context)


class ContactUs(View):
    context =   { 'name': 'Contact Us',
                      'description': 'Complete the form and send us a message. We will do our best to respond within 1 or 2 working days',
                      'form': forms.ContactUs,
                      'submit': u'Send'}

    def get(self, request):
        PageVisit.record(request)
        context = self.context.copy()
        context['form'] = context['form']()
        return render(request=request, template_name='base/SingleForm.html', context=context)

    def post(self,request):
        if request.POST.get('confirmation', False):
            return redirect(reverse('Home'))

        context = self.context.copy()
        form = context['form'](request.POST)
        if form.is_valid():
            data = form.cleaned_data

            # Message to the staff
            send_mail( subject="A message regarding {} from {}".format(data['reason'],data['sender_name']),
                       from_email = settings.DEFAULT_FROM_EMAIL,
                       recipient_list = [settings.DEFAULT_TO_EMAIL],
                       message = render_to_string(
                               'SuffolkCycleRide/emails/ContactUs_ToStaff',
                               context= dict( {'host':settings.BASE_URL,
                                            'reason_text': forms.ContactChoices.fullVersion(data['reason'])}.items() +\
                                            data.items() ) ))

            # Confirmation message back to the user
            send_mail( subject="The Great Suffolk Cycle Ride - Thank you for your message",
                       from_email = settings.DEFAULT_FROM_EMAIL,
                       recipient_list = [data['sender_email']],
                       message =render_to_string(
                               'SuffolkCycleRide/emails/ContactUs_ToStaff',
                               context = dict( {'host':settings.BASE_URL,
                                            'reason_text' :forms.ContactChoices.fullVersion(data['reason'])}.items() +\
                                            data.items() ) ) )

            return render(request=request,
                          template_name='base/SingleForm.html',
                          context={'confirmation':{'message':'Thank you for contacting us. Someone will be in touch soon'}})

        else:
            context['form'] = form
            return render(request=request,
                          template_name='base/SingleForm.html',
                          context= context)


def fundme(request, username):

    cyclist = get_object_or_404(cyclists.models.Cyclist, user__username = username)

    PageVisit.record(request=request, document_name='FundMe', user = cyclist.user )

    return render(request, 'SuffolkCycleRide/pages/fundme.html', context={'cyclist':cyclist, 'no_menu':True})