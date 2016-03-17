from django.conf.urls import include, url
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

from django.contrib import admin
admin.autodiscover()

import views

app_name = "home"

urlpatterns = [
    url(r'^$', views.home, name='Home'),
    url(r'^theevent$', views.the_event, name='TheEvent'),
    url(r'^SunriseFundraising$',
            TemplateView.as_view(template_name='SuffolkCycleRide/pages/SunriseFundraising.html'),
            name='SunriseFundraising$'),

    url(r'^getinvolved$', views.GetInvolved.as_view(), name="GetInvolved"),
    url(r'^contactus$', views.ContactUs.as_view(), name="ContactUs"),

    url(r'^privacy$', views.privacy, name='Privacy'),
    url(r'^FundMe/(?P<username>[0-9a-zA-Z]*)', views.fundme, name='FundMe'),

#    url(r'^technology$', TemplateView.as_view(template_name='SuffolkCycleRide/pages/technology.html'), name='Technology' ),

    url(r'^sponsorship/', include('Sponsors.urls', namespace='Sponsorship')),
    url(r'^User/', include("RegisteredUsers.urls", namespace='User')),
    url(r'^newsletter/', include("newsletter.urls", namespace="Newsletter")),
    url(r'^dashboard/', include("dashboard.urls", namespace="Dashboard")),
    url(r'^blog/', include('blog.urls', namespace='Blog')),
    url(r'^map_example', views.googlemap, name='Example'),

    url(r'^ol2map/', include('ol2map.urls', namespace='olMap2')), # Urls for mapping App -

    url(r'^markitup/', include('markitup.urls')),

    url(r'^admin/', include(admin.site.urls)),
]

if settings.DEBUG is True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

#Todo - implmenet 404 & 500 errors.
# http://stackoverflow.com/questions/17662928/django-creating-a-custom-500-404-error-page
