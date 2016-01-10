from django.conf.urls import include, url

from django.contrib import admin
admin.autodiscover()

from views import home, readmore, GetInvolved


urlpatterns = [
    url(r'^$', home, name='home'),
    url(r'^readmore$',readmore, name='Readmore'),
    url(r'^register/', include("RegisteredUsers.urls") ),
    url(r'^getinvolved/', GetInvolved.as_view(), name="GetInvolved"),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
]
