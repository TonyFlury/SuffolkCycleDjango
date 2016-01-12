from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.views.generic import View
from newsletter.forms import NewsletterSignUpForm
from RegisteredUsers.forms import NewUserForm, SignInForm

def home(request):
    """ The main pages page - currently a simple html page"""
    return render(request, "SuffolkCycleRide/pages/home.html",{})

def readmore(request):
    """The Read more page - currently a simple html page"""
    return render(request, "SuffolkCycleRide/pages/readmore.html", {} )

class GetInvolved(View):
    _forms = [  { 'name': 'Newsletter Sign Up',
                  'description': 'Do you want to keep informed, but not ready to sign up to take part. Then our newsletter is ideal for you.',
                  'form': NewsletterSignUpForm,
                  'submit': u'Send me the newsletter',
                  'prefix': 'nl' },
                { 'name': "Sign In",
                  'description': 'Do you have an account already - sign in here',
                  'form': SignInForm,
                  'submit': u'Sign In',
                  'prefix': 'si'},
                { 'name': 'Registration',
                  'description': 'Create an account here - your first step to participating or volunteering',
                  'form': NewUserForm,
                  'submit': u'Register',
                  'prefix': 'r'},
                ]

    def get(self, request):
        context = { "title" : "Suffolk Cycle Ride 2016 - Get Involved",
                    "forms": [ dict( [ (k,v if k != 'form' else v(prefix=f['prefix'])) for (k,v) in f.iteritems() if k != "prefix" ] )
                            for f in GetInvolved._forms],
                   }

        return render(request, "SuffolkCycleRide/base/VerticalForm.html", context=context)

    def post(self, request):

        context = { 'title': "Suffolk Cycle Ride 2016 - Get Involved",
                    'forms': [ dict( [ (k, (v if k != 'form' else (v() if f[u'submit'] != request.POST[u'submit']
                                                                        else v(request.POST, prefix=f['prefix']))))
                                       for (k,v) in f.iteritems() if k != "prefix" ] )
                            for f in GetInvolved._forms], }

        this_form = [ i['form'] for i in context['forms'] if i['submit'] == request.POST['submit'] ][0]

        if this_form.is_valid():
            this_form.save()

            print request.POST

            if  u'Sign In' in request.POST[u'submit'] :
                return HttpResponse("Signed In")
            if u'Send me the newsletter' in request.POST[u'submit'] :
                return HttpResponse("Signed up for the newsletter")
            elif u'Register' in request.POST[u'submit'] :
                return HttpResponse("New User Created")

        return render(request, "SuffolkCycleRide/base/VerticalForm.html", context=context)


