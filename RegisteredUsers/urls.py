from django.conf.urls import include, url

from django.contrib import admin
from RegisteredUsers.views import NewUser

admin.autodiscover()

urlpatterns = [
    url(r'^new$', NewUser.as_view(), name='Register.User'),
    ]
