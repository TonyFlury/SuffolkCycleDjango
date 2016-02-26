from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.conf import settings

from django.http import HttpResponseRedirect
from django.views.generic import View
from django.core.urlresolvers import reverse

from newsletter.forms import NewsletterSignUpForm
from RegisteredUsers.forms import NewUserForm
from newsletter.models import Newsletter
from stats.models import PageVisit
from django.core.mail import send_mail

from MultipleFormMixin import MultipleFormMixin

from context_processor import settings_base_url
import forms


# noinspection PyIncorrectDocstring
def home(request):
    """ The front page - where everybody first lands"""
    PageVisit.record(request)
    return render(request, "SuffolkCycleRide/pages/home.html", context={} )


# noinspection PyIncorrectDocstring
def readmore(request):
    """The Read more page - a list of the newsletter posts"""
    PageVisit.record(request)
    dl_url = reverse('newsletter:Download',kwargs = {'id':'0000'}).strip('0')
    qs = Newsletter.objects.order_by('-pub_date')
    return render(request, "SuffolkCycleRide/pages/readmore.html", context={'newsletter':qs, "dl_base":dl_url})


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
                               context = {
                                   'email': sub.email,
                                   'readmore_url': request.build_absolute_uri( reverse('Readmore') )
                               })

            if self.this_form.prefix == 'r':
                PageVisit.record(request, sub_document='New User Reqistration')
                user = self.this_form.save()
                send_mail( from_email = settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[ user.email ],
                            subject="Welcome to the Great Suffolk Cycle Ride",
                            message=render_to_string( "RegisteredUsers/Email/NewUserConfirmation.txt",
                                    context=dict( {'user': user,
                                             'ResetUrl': request.build_absolute_uri( reverse("User:ResetRequest") ),
                                             'HOST': request.get_host() },
                                             **settings_base_url(request)
                                             )
                                        ))
                self.this_form.login(request)
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
            return redirect(reverse('home'))

        context = self.context.copy()
        form = context['form'](request.POST)
        if form.is_valid():
            data = form.cleaned_data

            # Message to the staff
            send_mail( subject="A message regarding {} from {}".format(data['reason'],data['sender_name']),
                       from_email = settings.DEFAULT_FROM_EMAIL,
                       recipient_list = [settings.DEFAULT_TO_EMAIL],
                       message = render_to_string('SuffolkCycleRide/emails/ContactUs_ToStaff',
                                  context= dict( {'host':settings.BASE_URL,
                                                 'reason_text': forms.ContactChoices.fullVersion(data['reason'])},
                                                **data ) ))

            # Confirmation message back to the user
            send_mail( subject="The Great Suffolk Cycle Ride - Thank you for your message",
                       from_email = settings.DEFAULT_FROM_EMAIL,
                       recipient_list = [data['sender_email']],
                       message =render_to_string('SuffolkCycleRide/emails/ContactUs_ToStaff',
                                    context = dict( {'host':settings.BASE_URL,
                                                      'reason_text' :forms.ContactChoices.fullVersion(data['reason'])},
                                                  **data ) ) )

            return render(request=request,
                          template_name='base/SingleForm.html',
                          context={'confirmation':{'message':'Thank you for contacting us. Someone will be in touch soon'}})

        else:
            context['form'] = form
            return render(request=request,
                          template_name='base/SingleForm.html',
                          context= context)
