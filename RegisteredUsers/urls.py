from django.conf.urls import url
from django.contrib import admin
from views import SignIn, SignOut, ResetRequestView, Reset
from django.views.generic import TemplateView
admin.autodiscover()

urlpatterns = [
    url(r'^SignIn$', SignIn.as_view(), name='SignIn'),
    url(r'^SignOut$', SignOut, name='SignOut'),
    url(r'^ResetRequest$', ResetRequestView.as_view(), name='ResetRequest'),
    url(r'^Reset/([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$', Reset.as_view(), name='Reset'),
    url(r'^Reset/(.*)$', TemplateView.as_view(template_name='RegisteredUsers/pages/UnknownReset.html'), name='Reset'),
    ]

    #Todo - Refactor Reset to use SingleForm and confirmation popup (including for errors) - rather than custom templates
