from django.conf.urls import include, url

from django.contrib import admin
from views import SignIn, SignOut, ResetRequestView, Reset

admin.autodiscover()

urlpatterns = [
    url(r'^SignIn$', SignIn.as_view(), name='SignIn'),
    url(r'^SignOut$', SignOut, name='SignOut'),
    url(r'^ResetRequest$', ResetRequestView.as_view(), name='ResetRequest'),
    url(r'^Reset/([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$', Reset.as_view(), name='Reset'),
    ]
