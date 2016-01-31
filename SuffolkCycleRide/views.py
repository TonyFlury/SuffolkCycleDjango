from django.shortcuts import render
from django.template.loader import render_to_string

from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy, reverse
from EmailPlus.email import Email

from newsletter.forms import NewsletterSignUpForm
from RegisteredUsers.forms import NewUserForm
from newsletter.models import Newsletter
from stats.models import PageVisit

from MultipleFormMixin import MultipleFormMixin

from pprint import pprint

def home(request):
    """ The front page - where everybody first lands"""
    PageVisit.record(request)
    return render(request, "SuffolkCycleRide/pages/home.html", context={} )


def readmore(request):
    """The Read more page - a list of the newsletter posts"""
    PageVisit.record(request)
    dl_url = reverse('newsletter:Download',kwargs = {'id':'0000'}).strip('0')
    qs = Newsletter.objects.order_by('-pub_date')
    return render(request, "SuffolkCycleRide/pages/readmore.html", context={'newsletter':qs, "dl_base":dl_url})

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

    _forms = [  { 'name': 'Newsletter Sign Up',
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
                               context = {
                                   'email': sub.email,
                                   'readmore_url': request.build_absolute_uri( reverse('Readmore') )
                               })

            if self.this_form.prefix == 'r':
                PageVisit.record(request, sub_document='New User Reqistration')
                user = self.this_form.save()
                Email(subject="Welcome to the Great Suffolk Cycle Ride",
                        body=render_to_string("RegisteredUsers/Email/NewUserConfirmation.txt",
                                        context={'first_name': user.first_name,
                                                 'username': user.username,
                                                 'ResetUrl': request.build_absolute_uri( reverse("User:ResetRequest") ),
                                                 'HOST': request.get_host()
                                                 })
                                        ).send(user.email)
                self.this_form.login(request)
                return HttpResponseRedirect( reverse('Dashboard:Home') )

        return render(request, "base/VerticalForm.html", context=self.context)


