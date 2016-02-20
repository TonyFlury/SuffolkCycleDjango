from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.views.generic import View
from django.db.models import Q, F, Count, Case, When, Avg, Value, CharField
import calendar
from collections import Counter

from aggregates import StdDev, Mode

# Create your views here.

import models


class BlogMixin(object):
    max_per_page = 10            # Number normally allowed per page
    pagination_orphans = 5       # Minimum allowed per page

    def get_archive(self, request, display_year=None, display_month=None):
        """ Generate a query set which list which provides a calendarised archive

            :param request : The WSGI request which triggers this archive display, used to identify if draft documents should be displayed.
            :param display_year : The year (integer or None) which should be opened by default when this archive is displayed
            :param display_month : The month (integer or None) which should be opened by default when this archive is displayed
        """
        # Archive list consists of every published post - regardless of filtering
        archive = models.Entry.objects.filter(is_published = True).order_by("-pub_date")

        if not archive:
            return {'list': archive, 'display_year': None, 'display_month' : None }

        # Normalise display_year and display_month arguments if not given : default to the most recent entry
        if display_year is None and display_month is None:
            display_year, display_month = archive[0].pub_date.year, archive[0].pub_date.month
        elif display_year is not None and display_month is None:
            # If displaying a year only - get the latest entry in that year to determine the month.
            display_month =  archive.filter(pub_date__year = display_year).order_by("-pub_date")[0].pub_date.month

        return {'list':archive, 'display_year':display_year, 'display_month':display_month}

    def get_tag_cloud(self):
        """ Fetch the tag cloud data - categorise the Tags as upper, Average or lower
            Categorisation based on whether they are above or below average (mean)
            Maybe better to use MODE - i.e. the most frequent count.
            Using mode ensures that the largest number of labels are in the 'average' category
        """
        data = models.Tag.objects.\
            annotate(num_entries = Count('entries')).\
            filter(num_entries__gt = 0).aggregate(mode=Mode('num_entries'), mean=Avg('num_entries'), std_dev=StdDev('num_entries'))

        mode, mean, std_dev = data['mode'], data['mean'], data['std_dev']
        if not mode and not mean and not std_dev:
            return []

        # Fetch all the relevant tags, filtering out Tags with no entries,
        # and recording categories based on the Average & std_dev
        # Scope for category above upper (mean + 2*std_dev) etc

        return models.Tag.objects.\
                    annotate(num_entries = Count('entries')).\
                    filter(num_entries__gt = 0).\
                    annotate(category=Case(
                                When(num_entries__gt = mean+std_dev, then=Value('upper')),
                                When(num_entries__lt = mean-std_dev, then=Value('lower')),
                                default=Value('avg'),
                                output_field = CharField() ) )

    def pagination(self, query_set, page, url_args):
        """  Split the query set into pages based on the instance paging attributes
        :param query_set : The fully ordered query set of all the posts filtered by Tag or date
        :param page : The page being requested
        :param url_args : The set of arguments required to create the url
        :return A tuple of the query_set, the url for the previous page, and a url for the next page
        """
        if not query_set:
            return query_set, None, None, 0

        # Calculate all the pagination settings
        total = query_set.count()

        # How many complete pages - and how many left over (potentially)
        total_pages, orphans = divmod(total, self.max_per_page)

        # Work out where we need to start - it will only ever be the last page which will have orphans
        start_elem = (page-1)*self.max_per_page
        remaining = total - (page-1) * self.max_per_page  # How many entries are left to display from this page on

        if remaining >= (self.max_per_page + self.pagination_orphans):
            query_set, next_page, prev_page = (query_set[start_elem:start_elem + self.max_per_page], page+1, page-1 if page > 1 else None)
        else:
            query_set, next_page, prev_page = (query_set[start_elem:], None, page-1 if page > 1 else None)

        return query_set, prev_page, next_page, total_pages if orphans < self.pagination_orphans else total_pages + 1


class Main(BlogMixin,View):
    template = "blog/entry_list.html"
    max_per_page = 10              # Number normally allowed per page
    pagination_orphans = 5         # Minimum allowed per page

    def get(self, request, page=0, tag_slug=None, year=None, month=None):

        # Dictionary for arguments to be passed to queryset and pages - need two distinct dictionaries
        query_args, page_args = {}, {}

        # Normalise the current page
        page = int(page) if page else 1

        if tag_slug:
            query_args['tags__slug'] = page_args['tag_slug'] = tag_slug
        else:
            if year:
                query_args['pub_date__year'] = page_args['year'] = year
                if month :
                    query_args['pub_date__month'] =  page_args['month'] = month

        # Build the queryset - filter by the relevant arguments,
        qs = models.Entry.objects.filter(**query_args)

        # furthering filtering  depends on whether this user has their own unpublished posts
        if not request.user.is_anonymous():
            qs = qs.filter( Q(is_published = True) | Q( is_published=False, author = request.user ))
        else:
            qs = qs.filter( is_published = True )

        qs = qs.order_by( "is_published", "-pub_date")

        # Split the query set into pages : discard the page_count information for now.
        qs, page_args['prev_page'], page_args['next_page'], _ = self.pagination(qs, page, page_args)

        return render(request,self.template, context={
                                    'entries': qs,
                                    'archive': self.get_archive( request, int(year) if year else None,
                                                                          int(month) if month else None ),
                                    'tags': self.get_tag_cloud(),
                                    'args': page_args })


class Detail(BlogMixin,View):

    template = "blog/entry_detail.html"

    def get(self, request, slug):

        name = "blog:Detail"

        entry = models.Entry.objects.get(slug = slug)

        return render(request,self.template, context={
                                    'entry': entry,
                                    'archive': self.get_archive(request, entry.pub_date.year,entry.pub_date.month),
                                    'tags': self.get_tag_cloud(),
                                    'next_url': None,
                                    'prev_url': None,
                                    'args': {} })
