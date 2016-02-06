from django.conf.urls import include, url

from django.contrib import admin
admin.autodiscover()

from views import Main, Detail

app_name = "blog"

urlpatterns = [

    # Main view with optional page
    url(r'^$', Main.as_view(), name="Main"),
    url(r'^page/(?P<page>\d+)$', Main.as_view(), name="Main"),

    # Direct access by slug (one article - no paging)
    url(r'^article/(?P<slug>[\w-]+)$', Detail.as_view(), name="Detail"),

    # Search by tag (main article - supports paging)
    url(r'^search/(?P<tag_slug>[\w-]+)$', Main.as_view(), name="Search"),
    url(r'^search/(?P<tag_slug>[\w-]+)/page/(?P<page>\d+)$', Main.as_view(), name="Search"),

    # Search by date with paging
    url(r'^archive/(?P<year>\d{4})/$', Main.as_view(), name="Archive"),
    url(r'^archive/(?P<year>\d{4})/page/(?P<page>\d+)$', Main.as_view(), name="Archive"),
    url(r'^archive/(?P<year>\d{4})/(?P<month>\d{2})$', Main.as_view(), name="Archive"),
    url(r'^archive/(?P<year>\d{4})/(?P<month>\d{2})/page/(?P<page>\d+)$', Main.as_view(), name="Archive"),
]
