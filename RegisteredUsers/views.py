from django.shortcuts import render

from django.forms import ModelForm, PasswordInput, Form, CharField
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.views.generic import View
from newsletter.models import NewsletterSignUp

from email import EmailTypes, Email

# Simple View for User Registration - maybe never used on it's own.
class NewUser(View):
    def get(self, request):
        form = NewUserForm()
        return render(request, "RegisteredUsers/RegisterUser.html", {'FormContent': form,})

    def post(self, request):
        form = NewUserForm(request.POST)

        print form

        # If data is valid, proceeds to create a new post and redirect the user
        if form.is_valid():
            d = dict([(k,v) for k,v in form.cleaned_data.iteritems()])
            print d
            user = User.objects.create_user( **d )

            Email(EmailTypes.NewUserConfirmation).send(user)

            return HttpResponse("Saved")
            # return HttpResponseRedirect(reverse('post_detail', kwargs={'post_id': post.id}))
        else:
            return render(request, "RegisteredUsers/RegisterUser.html", {'FormContent': form,})