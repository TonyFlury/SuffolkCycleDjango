import os.path

from django.conf import settings
from django.shortcuts import render
from django.views.generic import View
from forms import NewsletterUnsubscribeForm, NewsletterUploadForm
from django.core.urlresolvers import reverse_lazy, reverse
from django.http import HttpResponse

from models import Newsletter
from stats.models import PageVisit

# noinspection PyIncorrectDocstring
def main(request):
    """The Read more page - a list of the newsletter posts"""
    PageVisit.record(request)
    dl_url = reverse('Newsletter:Download',kwargs = {'id':'0000'}).strip('0')
    qs = Newsletter.objects.order_by('-pub_date')
    return render(request, "newsletter/pages/newsletter.html", context={'newsletter':qs, "dl_base":dl_url})

#ToDo Rewrite Readmore page - to point to all the extra content

class Unsubscribe(View):
    context = { 'heading': 'Unsubscribe from the Newsletter',
                    'description': "Enter your email in order to stop receiving our newsletter. We are sorry that you no longer want to keep in touch.",
                    'submit': 'Un-subscribe',
                    'action': reverse_lazy('Newsletter:Unsubscribe'),
                    }

    def get(self, request, email):
        form = NewsletterUnsubscribeForm(data={'email':email})
        self.context['form'] = form
        return render(request, "base/SingleForm.html", context=self.context)

    def post(self, request, email):
        form = NewsletterUnsubscribeForm(request.POST)

        if form.is_valid():
            PageVisit.record(request)  # Only record successfull unsubscribes
            success = form.save()
            if success:
                return render( request, "newsletter/pages/unsubscribe.html",
                               context={'email': form.cleaned_data['email']} )

        self.context['form'] = form
        return render(request, "base/SingleForm.html", context=self.context)


class Upload(View):
    context = { 'heading': 'Upload a newsletter',
                    'description': "Choose an newsletter file (pdf ideally) to upload, ready to distribute.",
                    'submit': 'Upload',
                    'form_enctype': 'enctype="multipart/form-data"',
                    }
    def get(self, request):
        PageVisit.record(request)
        self.context['form'] = NewsletterUploadForm()
        return render(request, 'base/SingleForm.html', context=self.context)

    def post(self, request):
        form = NewsletterUploadForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponse("File Uploaded")

        self.context['form'] = form
        return render(request, 'base/SingleForm.html', context=self.context)


def Download(request, id ):
    PageVisit.record(request)
    nl = Newsletter.objects.get(reset_uuid=id)
    path = os.path.join(settings.MEDIA_ROOT, nl.content.name)
    name = os.path.basename(nl.content.name)
    d = open(path,"rb").read()
    response = HttpResponse(d, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(name)
    return response