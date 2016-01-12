from django.contrib.auth.models import User
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.shortcuts import render
from django.views.generic import View

from django.conf import settings

from EmailPlus.email import Email
from forms import NewUserForm


# Simple View for User Registration - maybe never used on it's own.
class NewUser(View):
    def get(self, request):
        form = NewUserForm()
        return render(request, "EmailPlus/RegisterUser.html", {'FormContent': form,})

    def post(self, request):
        form = NewUserForm(request.POST)

        # If data is valid, proceeds to create a new post and redirect the user
        if form.is_valid():
            d = dict([(k,v) for k,v in form.cleaned_data.iteritems()])
            print d
            user = User.objects.create_user( **d )

            Email( subject="Welcome to the Great Suffolk Cycle Ride1",
                   body = render_to_string("RegisteredUsers/Email/NewUserConfirmation.txt",
                           context = {'first_name': user.first_name,
                              'base_url':settings.BASE_URL,
                              'username': user.username
                                    } )
                   ).send(user.email)

            return HttpResponse("Saved")
            # return HttpResponseRedirect(reverse('post_detail', kwargs={'post_id': post.id}))
        else:
            return render(request, "EmailPlus/RegisterUser.html", {'FormContent': form,})