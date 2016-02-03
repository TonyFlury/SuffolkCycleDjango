from django.conf.urls import include, url
from django.views.generic import TemplateView

from django.contrib import admin
admin.autodiscover()

from views import home, readmore, GetInvolved

app_name = "home"

urlpatterns = [
    url(r'^$', home, name='Home'),
    url(r'^readmore$',readmore, name='Readmore'),
    url(r'^getinvolved$', GetInvolved.as_view(), name="GetInvolved"),
    url(r'^technology$', TemplateView.as_view(template_name='SuffolkCycleRide/pages/technology.html') ),
    url(r'^RegisteredUsers/', include("RegisteredUsers.urls", namespace='User')),
    url(r'^newsletter/', include("newsletter.urls", namespace="newsletter") ),
    url(r'^dashboard/', include("dashboard.urls", namespace="Dashboard")),
    url(r'^blog/', include('blog.urls', namespace='blog')),

    url(r'^markitup/', include('markitup.urls')),

    url(r'^admin/', include(admin.site.urls)),
]
